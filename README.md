# messenger-stats

Scripts to retrieve interesting stats on a person's messenger chat contents.
Note that data downloaded to Facebook will not contain messages you deleted
yourself (e.g. it is possible for you and your friend to have different
message counts for the same conversation).

This README is based on the data format as of 2022 Feb.

## Downloading Facebook Messenger Data

* Navigate to your Facebook Settings (top right menu) 
* Select Your Facebook Information in the left navbar. 
* Click `Show` on Download Your Information. 
* Select `JSON` for file format, and `low` for file quality (only affects photos)
* Choose the time period you want Facebook to retrieve your data from. 
* In Select Information to Download, click `Deselect All`, then select `Messages`. You can download other data, but only Messages is relevant for these scripts. 
* Request to download at the bottom. Depending on how much you use Messenger, it could take up to a day for Facebook to consolidated all of your data. 
* Once the data is ready, you will receive an email. Navigate back to the `Download Your Data` section.
* Go to `Available Files` on the top bar, and click `Download`. If you have multiple files, download the larger one. Or, download all the files and combine the folders (working on instructions for this).

## Scripts

Note: all scripts in this project are assumed to be run using `python3`.

* `messenger_stats.py` - entry point into the program. Include `-f [path]` to
  specify the path to the folder containing all the messages. Otherwise, the
  script assumes the folder `messages/inbox` exists in the working directory. Use `-h` to see all the options.

Example usage: `python3 messenger_stats.py -f path/to/inbox --sender_name "Bob Johnson"` 

## Ideas

* Participant activity pie chart
* Reacts given