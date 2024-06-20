import React, { useState } from 'react';
import axios from 'axios';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [questionAnswers, setQuestionAnswers] = useState([]);
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    // Clear previous messages and data
    setMessage('');
    setQuestionAnswers([]);
    setError('');
  };

  const handleFileUpload = async () => {
    if (!file) {
      setMessage('Please select a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/pdfs/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setMessage('File uploaded successfully!');
      console.log('File uploaded successfully:', response.data);

      // After successful upload, fetch question and answers
      fetchQuestionAnswers();
    } catch (error) {
      if (error.response) {
        setMessage(`Error: ${error.response.data}`);
        console.error('Response error:', error.response.data);
      } else if (error.request) {
        setMessage('Error: No response from the server.');
        console.error('Request error:', error.request);
      } else {
        setMessage(`Error: ${error.message}`);
        console.error('Error:', error.message);
      }
    }
  };

  const fetchQuestionAnswers = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/get_question_answers');
      setQuestionAnswers(response.data);
    } catch (error) {
      setError('Failed to fetch question answers.');
      console.error('Fetch error:', error);
    }
  };

  return (
    <div>
      <input type="file" onChange={handleFileChange} accept="application/pdf" />
      <button onClick={handleFileUpload}>Upload</button>
      {message && <p>{message}</p>}
      {error && <p>{error}</p>}
      {questionAnswers.length > 0 && (
        <div>
          <h2>Question and Answers</h2>
          <ul>
            {questionAnswers.map((qa, index) => (
              <li key={index}>
                <strong>Q: {qa.question}</strong>
                <br />
                A: {qa.answer}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
