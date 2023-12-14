import os
import ffmpeg

def compress_videos_in_folder(input_folder, output_folder):
    resolutions = {'1080p': {'size': '1920x1080', 'target_size': 50},
                   '720p': {'size': '1280x720', 'target_size': 40},
                   '360p': {'size': '640x360', 'target_size': 30}}

    video_files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))
                   and f.lower().endswith(('.mp4', '.avi', '.mkv'))]

    for file in video_files:
        input_path = os.path.join(input_folder, file)
        video_name = os.path.splitext(file)[0]

        for resolution, data in resolutions.items():
            probe = ffmpeg.probe(input_path)
            duration = float(probe['format']['duration'])

            original_size = os.path.getsize(input_path)
            original_bitrate = (original_size * 8) / (duration * 1024)

            target_size_percent = data['target_size']
            target_size = (target_size_percent / 100) * original_size

            video_bitrate = (target_size * 8) / (duration * 1024)
            audio_bitrate = max(min(256000, video_bitrate / 10), 32000)

            i = ffmpeg.input(input_path, threads=1)  # Limit threads to 1 for reduced performance usage

            output_file = f'{output_folder}/{video_name}/{resolution}/{video_name}_{resolution}_compressed.mp4'

            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            ffmpeg.output(
                i,
                os.devnull,
                **{
                    'c:v': 'libx264',
                    'b:v': f'{video_bitrate}k',
                    'pass': 1,
                    'f': 'mp4',
                    'vf': f'scale={data["size"]}'
                }
            ).overwrite_output().run(quiet=True)  # Run FFmpeg quietly

            ffmpeg.output(
                i,
                output_file,
                **{
                    'c:v': 'libx264',
                    'b:v': f'{video_bitrate}k',
                    'pass': 2,
                    'c:a': 'aac',
                    'b:a': f'{audio_bitrate}k',
                    'vf': f'scale={data["size"]}'
                }
            ).overwrite_output().run(quiet=True)  # Run FFmpeg quietly

# Compress all videos in the input folder and save in folders based on resolution with varied sizes
compress_videos_in_folder('input_folder', 'output_folder')
