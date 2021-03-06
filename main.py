from PIL import Image, ImageSequence
import sys

def get_gif_frames_average_duration(gif):
    return int(round(sum([frame.info['duration'] for frame in ImageSequence.Iterator(gif)])/gif.n_frames,-1))

def get_gif_first_frame_duration(gif):
    return gif.info['duration']

def get_gif_frames_duration(gif):
    return [frame.info['duration'] for frame in ImageSequence.Iterator(gif)]

colors = {
    "white": (255,255,255),
    "red": (255,0,0),
    "green": (0,255,0),
    "blue": (0,0,255),
    "black": (0,0,0)
}

duration_calculation_modes = {
    "average": get_gif_frames_average_duration,
    "first": get_gif_first_frame_duration,
    "individual": get_gif_frames_duration
}

def get_gif_frames_and_duration(gif_filename,duration_calculation_mode):
    gif = Image.open(gif_filename)
    gif_frames = []
    gif_duration = duration_calculation_modes[duration_calculation_mode](gif)
    pal = gif.getpalette()
    canvas = gif.convert('RGBA')
    first = True
    for frame in ImageSequence.Iterator(gif):
        if first:
            dimensions = None
            first = False
        else:
            dimensions = frame.tile[0][1]
            if not frame.palette.dirty:
                frame.putpalette(pal)                
            frame = frame.crop(dimensions)
        
        canvas.paste(frame, dimensions, frame.convert('RGBA'))
        gif_frames.append(canvas.copy())
    return [gif_frames, gif_duration]

def add_progress_bar_to_images(gif_frames,bar_height,rgb_color):
    for frame_index, frame in enumerate(gif_frames):
        width, height = frame.size
        pixels = frame.load()
        for x in range(int(width*frame_index/len(gif_frames))):
            for y_offset in range(1,bar_height+1):
                pixels[x, height-y_offset] = rgb_color
    return gif_frames

def assemble_and_save_gif(target_filename,gif_duration,gif_frames):
    gif_frames[0].save(target_filename, format='GIF',
                   append_images=gif_frames[1:],
                   save_all=True,
                   duration=gif_duration, loop=0)

def parse_arguments(raw_arguments):
    arguments = {}
    positional_arguments = 0
    for raw_argument in raw_arguments:
        if '=' in raw_argument:
            key, value = raw_argument.split('=',1)
            arguments[key] = value
        else:
            arguments[positional_arguments] = raw_argument
            positional_arguments += 1
    return arguments

def main():
    arguments = parse_arguments(sys.argv)
    if 1 not in arguments:
        print('Error: At least 1 positional argument is required.')
        sys.exit()
    filename = arguments[1]
    rgb_color = colors[arguments['color']] if 'color' in arguments and arguments['color'] in colors else colors["blue"]
    bar_height = int(arguments['height']) if 'height' in arguments and arguments['height'].isnumeric() else 3
    output_file = arguments['out'] if 'out' in arguments else 'progress_bar_{}'.format(filename)
    duration_calculation_mode = arguments['duration-calculation-mode'] if 'duration-calculation-mode' in arguments and arguments['duration-calculation-mode'] in duration_calculation_modes else 'average'
    frames, durations = get_gif_frames_and_duration(filename,duration_calculation_mode)
    frames_with_progress_bar = add_progress_bar_to_images(frames,bar_height,rgb_color)
    assemble_and_save_gif(output_file,durations,frames_with_progress_bar)

if __name__ == '__main__':
    main()
