import h5py
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from matplotlib.colors import ListedColormap
from matplotlib import animation
from mpl_toolkits.axes_grid1 import make_axes_locatable


# Initialize
plt.rcParams["animation.ffmpeg_path"] = "C:/ffmpeg/bin/ffmpeg.exe"  # Set the path to FFmpeg


def get_extended_viridis(vals: int = 600) -> ListedColormap:
    """
    Generate an extended viridis colormap.

    Args:
        vals (int): Number of color values. Default is 600.

    Returns:
        ListedColormap: A colormap object.
    """
    VIRIDIS_EXTENDED = [
        [0.0, 255, 200,100],
        [.13, 255, 153, 51],
        [.25, 230,  5,  40],
        [.38, 150,  3,  62],
        [0.5, 68,   1,  84],
        [.55, 72,  33, 115],
        [.59, 67,  62, 133],
        [.64, 56,  88, 140],
        [.68, 45, 112, 142],
        [.73, 37, 133, 142],
        [.77, 30, 155, 138],
        [.82, 42, 176, 127],
        [.86, 82, 197, 105],
        [.90, 34,  213, 73],
        [.95, 194, 223, 35],
        [1.0, 253, 231, 37]
    ]
    VE = np.array(VIRIDIS_EXTENDED)
    VE[:, 1:] = VE[:, 1:] / 256
    ve_list = []
    for i in range(1, len(VIRIDIS_EXTENDED)):
        pts = int((VE[i, 0] - VE[i - 1, 0]) * vals)
        ve_list.append(np.stack([np.linspace(VE[i - 1, 1], VE[i, 1], pts, endpoint=False),
                                 np.linspace(VE[i - 1, 2], VE[i, 2], pts, endpoint=False),
                                 np.linspace(VE[i - 1, 3], VE[i, 3], pts, endpoint=False)], axis=-1))
    VE = np.vstack(ve_list)
    return ListedColormap(VE)



def new_cbar_max(nm: float, pm: float) -> float:
    """
    Adjust maximum of colorbar using sqrt diff scaling.

    Args:
        nm (float): Negative maximum.
        pm (float): Positive maximum.

    Returns:
        float: Adjusted maximum.
    """
    if pm > nm:
        nm = nm + np.sqrt(pm - nm)
    return nm


def new_cbar_max_smooth(nm: float, pm: float) -> float:
    """
    Adjust maximum of colorbar using average scaling for a smoother effect.

    Args:
        nm (float): Negative maximum.
        pm (float): Positive maximum.

    Returns:
        float: Adjusted maximum.
    """
    if pm > nm:
        nm = (nm + pm) / 2
    return nm


def setup_visualization(axarr, plasma_steps, params, plot_order, cmap):
    """Setup initial chart objects."""
    ims, cxs, cbs, txs = [], [], [], []
    for i, ax in enumerate(axarr):
        ax.xaxis.set_tick_params(which="both", bottom=False, top=False, labelbottom=False)
        ax.yaxis.set_tick_params(which="both", bottom=False, top=False, labelbottom=False)
        cxs.append(make_axes_locatable(ax).append_axes("right", "5%", "1%"))
        ims.append(ax.imshow(plasma_steps[plot_order[i]][0], origin="lower", cmap=cmap))
        cbs.append(plt.colorbar(ims[i], cax=cxs[i]))
        txs.append(ax.set_title(f"{plot_order[i]}"))
    return ims, cxs, cbs, txs


def setup_figure(title: str):
    """
    Setup the figure for visualization.

    Args:
        title (str): Title for the figure.

    Returns:
        Tuple containing the figure and array of axes.
    """
    fig, axarr = plt.subplots(1, 3, figsize=(12, 4.35), sharex=True, sharey=True)
    fig.suptitle(title)
    return fig, axarr


def setup_animation(fig, axarr, plasma_steps, params, zero_omega, plot_order, cmap, pbar):
    ims, cxs, cbs, txs = setup_visualization(axarr, plasma_steps, params, plot_order, cmap)

    def animate(t):
        """Update data for animation."""
        for i, ax in enumerate(axarr):
            arr = plasma_steps[plot_order[i]][t]
            if zero_omega and plot_order[i] == "omega":
                arr -= np.mean(arr)
            vmax = np.max(arr)
            vmin = np.min(arr)
            pmin, pmax = ims[i].get_clim()
            pm = np.max([np.abs(pmin), pmax])
            nm = np.max([np.abs(vmin), vmax])
            nm = new_cbar_max(nm, pm)
            ims[i].set_data(arr)
            ims[i].set_clim(-nm, nm)
            txs[i].set_text(f"{plot_order[i]} (t={t*params['dt']:.4f})")
        pbar.update(1)
        #return ims

    return animate


def time_to_length(time: int, dt: float) -> int:
    """Convert time to length based on the given time step."""
    return int(round(time / dt))
 

def create_movie(
    input_filename: str,
    output_filename: str, 
    t0: int = 0,
    t1: int = None,
    zero_omega: bool=False,
    plot_order: list=["density", "omega", "phi"], 
    cmap: ListedColormap = get_extended_viridis(), 
    min_fps: float=10, 
    dpi: int=75, 
    speed: float=1
):
    # Setup details
    plasma_steps = h5py.File(input_filename, "r")
    params = dict(plasma_steps.attrs)
    title = generate_title(params)
    if t1 is None:
        t1 = (len(plasma_steps[plot_order[0]]) - 1) * params["frame_dt"]
    t0_idx = time_to_length(t0 - params.get('t0', 0), params["frame_dt"])
    t1_idx = time_to_length(t1 - params.get('t0', 0), params["frame_dt"])
    # Determine fps and step size to use
    fps = int(speed / params["frame_dt"])
    print(f"{speed}t/s  @  {params['frame_dt']} t/frame  implies {fps} frames/s")
    frame_steps = max(1, fps // min_fps)
    fps /= frame_steps
    print(f"with min_fps {min_fps} we take every {frame_steps} frames still generate {fps} frame/s")
    # Define Progress
    total = int((t1_idx - t0_idx) // frame_steps)
    frame_range = range(t0_idx, t1_idx + 1, frame_steps)
    pbar = tqdm(total=total, smoothing=0.3, mininterval=5)
    # Setup Figure & Animation
    fig, axarr = setup_figure(title)
    ims, cxs, cbs, txs = setup_visualization(axarr, plasma_steps, params, plot_order, cmap)
    fig.subplots_adjust(top=0.94, bottom=0, right=0.95, left=0.01, hspace=0, wspace=0.2)
    # Run Animation
    writer = animation.writers["ffmpeg"](fps=fps, metadata=dict(artist="Robin Greif"))
    #animate = setup_animation(fig, axarr, plasma_steps, params, zero_omega, plot_order, cmap, pbar)

    def animate(t):
        """Update data for animation."""
        for i, ax in enumerate(axarr):
            arr = plasma_steps[plot_order[i]][t]
            if zero_omega and plot_order[i] == "omega":
                arr -= np.mean(arr)
            vmax = np.max(arr)
            vmin = np.min(arr)
            pmin, pmax = ims[i].get_clim()
            pm = np.max([np.abs(pmin), pmax])
            nm = np.max([np.abs(vmin), vmax])
            nm = new_cbar_max_smooth(nm, pm)
            ims[i].set_data(arr)
            ims[i].set_clim(-nm, nm)
            txs[i].set_text(f"{plot_order[i]} (t={t*params['dt']:.4f})")
        pbar.update(1)

    ani = animation.FuncAnimation(fig, animate, frames=frame_range)
    # Save MOvie
    output_filename = f"{output_filename}_dpi={dpi}_fps={fps:.0f}_speed={speed:.0f}_t0={t0}_t1={t1}.mp4"
    ani.save(output_filename, writer=writer, dpi=dpi)
    plt.close()
    plasma_steps.close()
    print(f"{output_filename}")


def generate_title(params):
    return ",  ".join([
        f"c1={params['c1']}",
        #f"L={params['L']:.2f}",
        f"k0={params['k0']:.2f}",
        f"pts={params['grid_pts']:.0f}",
        f"dt={params['dt']}",
        f"N={params['N']:.0f}",
        f"nu={params['nu']:.2g}"
    ])

