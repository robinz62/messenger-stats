# messenger-stats

Scripts to retrieve interesting stats on a person's messenger chat contents.
Note that data downloaded to Facebook will not contain messages you deleted
yourself (e.g. it is possible for you and your friend to have different
message counts for the same conversation).

## Downloading Facebook Messenger Data

Navigate to your Facebook Settings (top right menu) then select Your Facebook
Information in the left navbar. Click Download Your Information. You can
download other data, but only Messages is relevant for these scripts. Be sure
to download the files as JSON.

## Scripts

* `messenger_stats.py` - entry point into the program. Include `-f [path]` to
  specify the path to the `messages` folder. Otherwise, the script assumes the
  folder exists in the working directory.

## Ideas

* per-person chat frequency timeline / timeseries