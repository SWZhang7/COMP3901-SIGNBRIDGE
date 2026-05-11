import React, { useRef, useEffect, useState } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';

const CameraView = ({ onTranslation }) => {
  const webcamRef = useRef(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [translation, setTranslation] = useState('');
  const [confidence, setConfidence] = useState(null);

  useEffect(() => {
    const interval = setInterval(() => {
      if (webcamRef.current && isCameraActive) {
        captureAndTranslate();
      }
    }, 100);

    return () => clearInterval(interval);
  }, [isCameraActive]);

  const captureAndTranslate = async () => {
    const imageSrc = webcamRef.current.getScreenshot();

    if (!imageSrc) return;

    try {
      const response = await axios.post('http://localhost:5000/predict-sign', {
        image: imageSrc
      });

      setTranslation(response.data.prediction);
      setConfidence(response.data.confidence);

      if (onTranslation) {
        onTranslation(response.data.prediction);
      }
    } catch (error) {
      console.error('Prediction error:', error);
    }
  };

  const videoConstraints = {
    width: 720,
    height: 480,
    facingMode: "user"
  };

  return (
    <div className="camera-container">
      <h2 className="camera-title">JSL Translator</h2>

      <div className="camera-preview">
        {isCameraActive ? (
          <Webcam
            ref={webcamRef}
            audio={false}
            screenshotFormat="image/jpeg"
            videoConstraints={videoConstraints}
            className="camera-video"
          />
        ) : (
          <div className="camera-placeholder">
            <p>Camera is off</p>
          </div>
        )}

        <div className="camera-controls">
          <button
            onClick={() => setIsCameraActive(!isCameraActive)}
            className={`btn ${isCameraActive ? 'btn-danger' : 'btn-primary'}`}
          >
            {isCameraActive ? 'Stop Camera' : 'Start Camera'}
          </button>
        </div>
      </div>

      <div className="translation-box">
        <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.5rem' }}>
          Translation:
        </h3>

        <p className="translation-text">
          {translation || 'Waiting for sign language input...'}
        </p>

        {confidence !== null && (
          <p style={{ fontSize: '0.9rem', opacity: 0.8 }}>
            Confidence: {(confidence * 100).toFixed(1)}%
          </p>
        )}
      </div>
    </div>
  );
};

export default CameraView;