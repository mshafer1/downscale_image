# downscale_image
A utility to downscale an image to the desired file size.

Relies on an install of ffmpeg to incrementing downscale the image file into a new file.

This modules provides the script `downscale-image`

```
> downscale-image --help
Usage: downscale-image [OPTIONS] IN_FILE

  Downscale in_file to desired max-size.

Options:
  --max-size INTEGER RANGE   Max output size (in MB)  [default: 2; x>0]
  --add-to-right-click-menu  (Windows only) Register this program in right
                             click menu for supported file types.
  --help                     Show this message and exit.
```
