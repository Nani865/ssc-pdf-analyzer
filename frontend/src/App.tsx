import React, { useState } from 'react';
import './App.css';

function App() {
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    setLoading(true);
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000/api'}/papers/upload`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setUploadedFiles(data.uploaded_files || []);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>SSC PDF Analyzer</h1>
        <p>AI-powered question extraction and analysis</p>
      </header>
      
      <main className="App-main">
        <section className="upload-section">
          <h2>Upload PDF Files</h2>
          <div className="upload-area">
            <input
              type="file"
              multiple
              accept=".pdf"
              onChange={handleFileUpload}
              disabled={loading}
            />
            {loading && <p>Uploading...</p>}
          </div>
        </section>

        {uploadedFiles.length > 0 && (
          <section className="results-section">
            <h2>Uploaded Files</h2>
            <ul>
              {uploadedFiles.map((file, index) => (
                <li key={index}>{file}</li>
              ))}
            </ul>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
