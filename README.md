# LabelMaker

## Quickly and easily create Audacity-friendly labels files using Slack

This app takes advantage of Slack's built-in transcription functionality to create a plain-text file that can be imported as "labels" into Audacity -- the free, open-source digital audio workstation (DAW).

Here's how it works. 

### Step 1 -- Acquire Audio

Record your audio in Audacity. 

![Screenshot of an Audacity project with a roughly minute-long audio track.](https://github.com/torontocaper/LabelMaker/assets/79330948/5f176bf5-9769-4dcb-aff0-20a66b5700d6)

When you're finished, export the audio -- preferably as an mp3. 

(note: you can use audio from another source, as long as you import it into Audacity at some point.)

### Step 2 -- Upload Audio to Slack

As mentioned, this app takes advantage of Slack's built-in transcription service, so we need to get our audio into Slack. 

Luckily, this is as simple as sending a message with an attachment.

![Screenshot shows the exported audio file being uploaded to Slack.](https://github.com/torontocaper/LabelMaker/assets/79330948/b7cacbba-55a3-45c4-ac4f-de2956f57e79)

Now we're ready to invoke the app. 

### Step 3 -- React to your post with the "label" emoji (🏷️)

This sends a "POST" request the app's "Slack/Events" endpoint, triggering the actual label-making part.

![Screenshot shows a Slack post with the "label" reaction, followed by replies from the LabelMaker app.](https://github.com/torontocaper/LabelMaker/assets/79330948/a4d70124-d071-4cc8-8802-a572a6042b03)

After a few seconds or minutes (depending on the length of the file), you should get a response from the LabelMaker app.

At this point, you can download the "labels" file and bring it into Audacity.

### Step 4 -- Import your labels into Audacity

Now we bring our labels into Audacity so that our transcript lines up with our audio.

It's as simple as clicking File/Import/Labels... in the Audacity toolbar.

![Screenshot shows the audio file with the transcript slong the bottom.](https://github.com/torontocaper/LabelMaker/assets/79330948/c4719e44-86a3-4ed1-8c44-2f09bdc3150d)

Hopefully this makes it easier to identify the parts of your audio you want to save.

Please get in touch with any feedback, or if you'd like to install this app to your Slack workspace!
