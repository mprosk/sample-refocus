# sample-refocus
Script for cleaning up and re-encoding sample libraries, most specifically [this scrape of samplefocus.com](https://maia.crimew.gay/samples/)

**Usage**

```
$ python -m refocus [-h] [--rename] [--rate RATE] {copy,convert,touch,dry} source output
```

**Modes**

`dry` -- don't actually copy any files. will create the folder structure

`touch` -- "touch"-es the output files, creating a zero-byte file of the correct name

`copy` -- copies the files to the output directory

`convert` -- converts the source files into WAVs. Requires `ffmpeg`

**Positional arguments**
`source`  -- root directory containing the files to process. subfolders are recursed automatically
`output` -- target directory in which to put processed files

**Options**
`-h, --help` -- shows the help message and exits
`--rename` -- if set, filenames will be cleaned up
`--rate RATE` -- sample rate of the output WAV files. Only applies if using `convert` mode. 



### Examples

Clean up the file names:

```
$ python -m refocus copy --rename ./samples ./samples_cleaned
```

Clean up the file names and convert to 26kHz WAV:

```
$ python -m refocus convert --rename --rate 26000 ./samples ./samples_cleaned_lofi
```

