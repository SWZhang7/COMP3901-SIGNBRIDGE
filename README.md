# SIGNBRIDGE

SIGNBRIDGE is a real-time Jamaican Sign Language recognition system that uses a webcam to detect and translate hand signs into text and speech.

The system is able to recognize:

- static one-hand signs (letters)
- one-hand motion-based words (like J and Z)
- two-hand motion-based phrases

The goal of the project is to bridge communication by converting sign input into readable text and spoken output in real time.

## What the Program Does

The program captures live video from your webcam and uses MediaPipe to detect hand, face, and body landmarks.

These landmarks are processed and passed into trained machine learning models to classify the sign being performed. The system then:

- displays the detected output on screen
- adds it to a conversation/history panel
- speaks the output using text-to-speech

The system prioritizes detection in this order:
1. two-hand phrases
2. one-hand motion words
3. static signs

## Installations Required

Make sure you have Python installed (Python 3.8 or higher recommended).

Best recommended 3.10 

Install the required libraries using:

```bash
pip install opencv-python mediapipe numpy joblib pyttsx3
```





# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
