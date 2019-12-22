# messenger-stats

Scripts to retrieve interesting stats on a person's messenger chat contents.
Note that data downloaded to Facebook will not contain messages you deleted
yourself (e.g. it is possible for you and your friend to have different
message counts for the same conversation).

The code and README is based on Facebook's exported data format as of Dec 2019.

## Downloading Facebook Messenger Data

Navigate to your Facebook Settings (top right menu) then select Your Facebook
Information in the left navbar. Click Download Your Information. You can
download other data, but only Messages is relevant for these scripts. Be sure
to download the files as JSON. This program doesn't process any media, so feel
free to download that in low quality to reduce the download size.

## Running the Program

All files in this project are intended to be run using `python3`.

Example usage: `python3 messenger_stats.py`.

* Append `-f [path]` to specify the path to the folder containing all the
  messages. Defaults to `messages/inbox`.
* Documentation on additional argument can be found by running the program
  appended with `-h`.

## Ideas

* Participant activity pie chart / to vs from count
* Reacts given

* overlay different time graphs
* view char counts
* user interface / web app lol
