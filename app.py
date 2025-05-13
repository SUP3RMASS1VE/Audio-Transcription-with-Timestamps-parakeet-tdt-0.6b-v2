import gradio as gr
import torch
import pandas as pd
import nemo.collections.asr as nemo_asr
import os
from pathlib import Path
import tempfile

# Create a directory for example audio files if it doesn't exist
EXAMPLE_DIR = Path("examples")
EXAMPLE_DIR.mkdir(exist_ok=True)

# Function to load the parakeet TDT model
def load_model():
    # Load the model from HuggingFace
    print("Loading ASR model...")
    asr_model = nemo_asr.models.ASRModel.from_pretrained(model_name="nvidia/parakeet-tdt-0.6b-v2")
    print("Model loaded successfully!")
    return asr_model

# Global model variable to avoid reloading
model = None

def transcribe_audio(audio_file, progress=gr.Progress()):
    global model
    
    # Load the model if not already loaded
    if model is None:
        progress(0.1, desc="Loading model...")
        model = load_model()
    
    # Save the temporary audio file if it's from Gradio
    if isinstance(audio_file, tuple):
        temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_audio_path = temp_audio.name
        temp_audio.close()
        
        sample_rate, audio_data = audio_file
        import soundfile as sf
        sf.write(temp_audio_path, audio_data, sample_rate)
        audio_path = temp_audio_path
    else:
        audio_path = audio_file
    
    progress(0.3, desc="Transcribing audio...")
    
    # Transcribe with timestamps
    output = model.transcribe([audio_path], timestamps=True)
    
    # Extract segment-level timestamps
    segments = []
    
    # For CSV output
    csv_data = []
    
    # Convert timestamp info to desired format
    if hasattr(output[0], 'timestamp') and 'segment' in output[0].timestamp:
        for stamp in output[0].timestamp['segment']:
            segment_text = stamp['segment']
            start_time = stamp['start']
            end_time = stamp['end']
            
            segments.append({
                "text": segment_text,
                "start": start_time,
                "end": end_time
            })
            
            # Add to CSV data
            csv_data.append({
                "Start (s)": f"{start_time:.2f}",
                "End (s)": f"{end_time:.2f}",
                "Segment": segment_text
            })
    
    # Create DataFrame for CSV
    df = pd.DataFrame(csv_data)
    
    # Save CSV to a temporary file
    csv_path = "transcript.csv"
    df.to_csv(csv_path, index=False)
    
    # Full transcript
    full_text = output[0].text if hasattr(output[0], 'text') else ""
    
    progress(1.0, desc="Done!")
    
    # Clean up the temporary file if created
    if isinstance(audio_file, tuple) and os.path.exists(temp_audio_path):
        os.unlink(temp_audio_path)
    
    return full_text, segments, csv_path

def create_transcript_table(segments):
    if not segments:
        return "No segments found"
    
    html = """
    <style>
    .transcript-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }
    .transcript-table th, .transcript-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    .transcript-table th {
        background-color: #f2f2f2;
    }
    .transcript-table tr:hover {
        background-color: #f5f5f5;
        cursor: pointer;
    }
    </style>
    <table class="transcript-table">
        <tr>
            <th>Start (s)</th>
            <th>End (s)</th>
            <th>Segment</th>
        </tr>
    """
    
    for segment in segments:
        html += f"""
        <tr onclick="document.dispatchEvent(new CustomEvent('play_segment', {{detail: {{start: {segment['start']}, end: {segment['end']}}}}}))">
            <td>{segment['start']:.2f}</td>
            <td>{segment['end']:.2f}</td>
            <td>{segment['text']}</td>
        </tr>
        """
    
    html += "</table>"
    return html

def download_example():
    # URL for an example file - we'll use a sample from LibriSpeech
    url = "https://dldata-public.s3.us-east-2.amazonaws.com/2086-149220-0033.wav"
    import requests
    
    example_path = EXAMPLE_DIR / "example-audio.wav"
    if not example_path.exists():
        print(f"Downloading example audio to {example_path}...")
        response = requests.get(url)
        with open(example_path, 'wb') as f:
            f.write(response.content)
    
    return str(example_path)

# Define custom JavaScript to handle segment playback
js_code = """
function(audio) {
    document.addEventListener('play_segment', function(e) {
        const audioEl = document.querySelector('audio');
        if (audioEl) {
            audioEl.currentTime = e.detail.start;
            audioEl.play();
            
            // Optional: Stop at segment end
            const stopAtEnd = function() {
                if (audioEl.currentTime >= e.detail.end) {
                    audioEl.pause();
                    audioEl.removeEventListener('timeupdate', stopAtEnd);
                }
            };
            audioEl.addEventListener('timeupdate', stopAtEnd);
        }
    });
    return audio;
}
"""

# Create Gradio interface
with gr.Blocks(css="footer {visibility: hidden}") as app:
    gr.Markdown("# Audio Transcription with Timestamps")
    gr.Markdown("Upload an audio file or record audio to get a transcript with timestamps")
    
    with gr.Row():
        with gr.Column():
            with gr.Tab("Upload Audio File"):
                audio_input = gr.Audio(type="filepath", label="Upload Audio File")
            
            with gr.Tab("Microphone"):
                audio_record = gr.Audio(sources=["microphone"], type="filepath", label="Record Audio")
            
            example_btn = gr.Button("Load Example Audio")
            transcribe_btn = gr.Button("Transcribe Uploaded File", variant="primary")
        
        with gr.Column():
            full_transcript = gr.Textbox(label="Full Transcript", lines=5)
            transcript_segments = gr.JSON(label="Segments Data", visible=False)
            transcript_html = gr.HTML(label="Transcript Segments (Click a row to play)")
            csv_output = gr.File(label="Download Transcript CSV")
            audio_playback = gr.Audio(label="Audio Playback", elem_id="audio_playback", interactive=False)
    
    # Set up event handlers
    example_btn.click(download_example, outputs=audio_input)
    
    # Handle transcription from file upload
    transcribe_btn.click(
        transcribe_audio, 
        inputs=[audio_input],
        outputs=[full_transcript, transcript_segments, csv_output]
    )
    
    # Handle transcription from microphone
    audio_record.stop_recording(
        transcribe_audio,
        inputs=[audio_record],
        outputs=[full_transcript, transcript_segments, csv_output]
    )
    
    # Update the HTML when segments change
    transcript_segments.change(
        create_transcript_table,
        inputs=[transcript_segments],
        outputs=[transcript_html]
    )
    
    # Apply custom JavaScript for audio playback
    audio_input.change(
        lambda x: x,
        inputs=[audio_input],
        outputs=[audio_playback],
        js=js_code
    )
    
    audio_record.stop_recording(
        lambda x: x,
        inputs=[audio_record],
        outputs=[audio_playback],
        js=js_code
    )

# Launch the app
if __name__ == "__main__":
    app.launch() 