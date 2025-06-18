from mido import MidiFile, MidiTrack, MidiFile, Message
import sys

def split_channels(input_path):
    output_path = input_path.replace(".mid","") + "_output.mid"
    mid = MidiFile(input_path)
    output = MidiFile(ticks_per_beat=mid.ticks_per_beat)
    track_out = MidiTrack()
    output.tracks.append(track_out)

    # Arrange all note events in chronological order
    events = []
    for track in mid.tracks:
        abs_time = 0
        for msg in track:
            abs_time += msg.time
            events.append((abs_time, msg))

    events.sort(key=lambda x: x[0])

    current_time = 0
    last_abs_time = 0
    note_states = [None] * 16  # note status of each channels

    for abs_time, msg in events:
        delta = abs_time - last_abs_time
        last_abs_time = abs_time

        if msg.type == 'note_on' and msg.velocity > 0:
            for ch in range(16):
                if note_states[ch] is None:
                    note_states[ch] = msg.note
                    new_msg = msg.copy(channel=ch, time=delta)
                    track_out.append(new_msg)
                    break

        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            for ch in range(16):
                if note_states[ch] == msg.note:
                    note_states[ch] = None
                    new_msg = msg.copy(channel=ch, time=delta)
                    track_out.append(new_msg)
                    break

        else:
            # remains the same meta messages
            if msg.is_meta:
                track_out.append(msg.copy(time=delta))
            elif hasattr(msg, 'channel'):
                track_out.append(msg.copy(channel=msg.channel, time=delta))
            else:
                track_out.append(msg.copy(time=delta))

    output.save(output_path)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Specify the path of the MIDI file to be processed as an argument.")
    else:
        split_channels(sys.argv[1])
        print("Process Done" + sys.argv[1].replace(".mid","") + "_output.mid")
