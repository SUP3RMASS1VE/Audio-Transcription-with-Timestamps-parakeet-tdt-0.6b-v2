# Audio Transcription App with Parakeet-TDT-0.6b

This is a Gradio web application that uses NVIDIA's Parakeet-TDT-0.6b model for automatic speech recognition with timestamp functionality.

## Features

- Transcribe audio files with word-level timestamps
- Record audio directly through the microphone
- Interactive transcript with clickable segments that play the corresponding audio
- Download transcripts as CSV files with timestamps
- Example audio file included for testing

## Screenshot

![Screenshot 2025-05-13 142033](https://github.com/user-attachments/assets/8014d5a7-931a-47e3-9855-01f3f8bb934e)

## Setup and Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

   Note: This application requires Python 3.8+ and CUDA-compatible GPU for optimal performance.

3. Run the application:
   ```
   python app.py
   ```

4. Open your browser and navigate to the URL displayed in the terminal (typically http://127.0.0.1:7860)

## Usage

1. **Upload an audio file** or **Record audio** using the provided interfaces
2. Click the **Transcribe** button to process the audio
3. View the complete transcript and the segmented version with timestamps
4. Click on any segment in the table to play that specific portion of the audio
5. Download the transcript as a CSV file using the download button

## Model Information

This application uses NVIDIA's Parakeet-TDT-0.6b-v2 model:
- 600-million-parameter automatic speech recognition (ASR) model
- Supports punctuation, capitalization, and accurate timestamp prediction
- Trained on diverse English speech data
- More information: [Hugging Face Model Card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2)

## License

This project is licensed under the terms of the CC-BY-4.0 license, consistent with the model's license.

## Acknowledgements

- NVIDIA for creating and releasing the Parakeet-TDT model
- Hugging Face for hosting the model
- Gradio for the web interface framework 
