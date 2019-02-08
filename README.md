# messenger-stats

Scripts to retrieve interesting stats on a person's messenger chat contents.
Note that data downloaded to Facebook will not contain messages you deleted
yourself (e.g. it is possible for you and your friend to have different
message counts for the same conversation).

This README is based on the data format as of Feb 2019.

## Downloading Facebook Messenger Data

Navigate to your Facebook Settings (top right menu) then select Your Facebook
Information in the left navbar. Click Download Your Information. You can
download other data, but only Messages is relevant for these scripts. Be sure
to download the files as JSON.

## Scripts

Note: all scripts in this project are assumed to be run using `python3`.

* `messenger_stats.py` - entry point into the program. Include `-f [path]` to
  specify the path to the folder containing all the messages. Otherwise, the
  script assumes the folder `messages/inbox` exists in the working directory.

Example usage: `python3 messenger_stats.py -f path/to/inbox`

## Ideas

* Participant activity pie chart
* Reacts given