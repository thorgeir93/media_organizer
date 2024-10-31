# Media Organizer

**STILL in development phase**

**Media Organizer** is a Python tool designed to help users organize their media collection by date. By analyzing image metadata (EXIF) or filesystem properties, it moves media to directories named after the date the media were taken.

## Features

- Reads media metadata (EXIF) to get the accurate date.
- Falls back to file creation/modification date if metadata is unavailable.
- Special handling for Darktable `.xmp` configuration files.
- Supports multiple image formats.

## Development

```sh
pre-commit run --all-files
```

## Improvments/TODO
* Logging:
  * allow verbose, do not use `print`.
  * By default log to /tmp folder all the action made, to be able to undo things.
* Unittest: media_originizer.py arguments and more
* Add pre-commit: for static analysis
* If file already exist in destinition, allow extend the original file and move it, e.g. `IMG01.jpg` already exist, common renaming would be `IMG01 (1).jp`.
* Split up the code: remove file logic to anothe file and TEST it!
* Fix static analysis
* if a JPG/mp4 and it have been editid, move it to media/{photos,video}/export?
* We might want to find the original image if we have the xmp config file but not the original one in the same directory.

## How it Works

1. The script scans the source directory for all media files.
2. For each file, it attempts to fetch the date from:
   - EXIF data if available.
   - If EXIF data isn't available or the file isn't an image, it uses the file's creation or modification date.
   - For Darktable `.xmp` files, it retrieves the date from the associated image.
3. Once the date is determined, it moves the media file to a directory named after the date (e.g., `2023-05-20`).
4. If the target directory doesn't exist, it's created.
5. The file is then moved to the target directory.

## Handling Darktable `.xmp` Files

Darktable is a photography application that creates `.xmp` configuration files to store photo edit histories. If an `.xmp` file is encountered, the script:

- Derives the original media file name by stripping the `.xmp` suffix.
- Checks if the original media file exists in the same directory.
- Retrieves the date from the original media file.
- Moves the `.xmp` file to the appropriate date-named directory.


## Using the Media Organizer Script

### Script Parameters

- `--source` or `-s`: The directory where your unorganized media files are located.
- `--destination` or `-d`: The directory where you want the organized media to be saved to. If a directory with the same date already exists, the media will be added to that directory.

### Running the Script

1. Navigate to the root directory of the script.

2. Activate the virtual environment:

   ```bash
   poetry shell
   ```

3. Run the script with:

   ```bash
   poetry run python media_organizer.py --source /path/to/source/directory --destination /path/to/target/directory
   ```

Replace `/path/to/source/directory` with the path to your unorganized medias and `/path/to/target/directory` with the path to where you want the organized medias to be saved.

### Expected Outcome

Once the script runs successfully, you should find your photos and videos organized in the destination directory under folders named by their creation date. For instance:

```
destination-directory/
│
├── 2021-01-01/
│   ├── IMG001.jpg
│   ├── VID001.mp4
│   └── ...
│
├── 2021-01-02/
│   ├── IMG002.jpg
│   └── ...
│
└── ...
```

Darktable configuration files will be sorted based on the creation date of their corresponding images.


## Usage

```
usage: media_organizer.py [-h] [--fast] [--dry-run] [--overwrite] source_dir [dest_dir]

Organize media by date.

positional arguments:
  source_dir   Source directory containing images.
  dest_dir     Destination directory.

options:
  -h, --help   show this help message and exit
  --fast       Use fast mode. Less accurate but faster.
  --dry-run    Perform a dry run without actual moving.
  --overwrite  Use this flag to overwrite files in destinition folder, be careful! default is False.
```

## Real world example

```bash
# Navigate to root of the project
poetry shell
python media_organizer/media_organizer.py --dry-run ~/tmp
```

This command will not move files, just show what files will be moved and where.
If you remove the dry run flag, it will organize the media by moving the images/videos from `/home/thorgeir/tmp` to `/home/thorgeir/media/photos/2023` since the year 2023 is the current year.

## Author

Þorgeir Eyfjörð Sigurðsson
