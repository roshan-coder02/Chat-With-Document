import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import styled from 'styled-components';

const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

const DropzoneContainer = styled.div`
  border: 2px dashed ${({ $isDragActive, $hasFile }) =>
    $isDragActive ? '#007bff' : $hasFile ? '#4caf50' : '#ccc'};
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  background-color: ${({ $isDragActive }) =>
    $isDragActive ? 'rgba(0, 123, 255, 0.05)' : 'transparent'};
  transition: border-color 0.2s ease;
  margin-bottom: 20px;

  &:hover {
    border-color: ${({ $hasFile }) => ($hasFile ? '#4caf50' : '#007bff')};
  }
`;

const handleUpload = async (file) => {
  if (!file) {
    console.error("No file selected.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file); // Ensure correct key name matches FastAPI

  try {
    const response = await fetch(`${API_BASE_URL}/upload/`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const result = await response.json();
    console.log("Upload Success:", result);
  } catch (error) {
    console.error("Upload Error:", error);
  }
};



const FileUpload = ({ onFileUpload, currentFile }) => {
  const onDrop = useCallback(
    (acceptedFiles) => {
      const file = acceptedFiles[0];
      if (file)
      {
        onFileUpload(file);
        handleUpload(file);
      }
    },
    [onFileUpload]
  );

  const removeFile = useCallback(
    (e) => {
      e.stopPropagation();
      onFileUpload(null);
    },
    [onFileUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: 'application/pdf',
    maxFiles: 1,
    onDrop,
    disabled: !!currentFile,
  });

  return (
    <DropzoneContainer
      {...getRootProps()}
      $isDragActive={isDragActive}
      $hasFile={!!currentFile}
    >
      <input {...getInputProps()} />
      {currentFile ? (
        <div>
          <span>📄 {currentFile.name}</span>
          <button onClick={removeFile}>Remove</button>
        </div>
      ) : (
        <p>
          {isDragActive
            ? 'Drop the PDF here...'
            : "Drag 'n' drop a PDF here, or click to select"}
        </p>
      )}
    </DropzoneContainer>
  );
};

export default FileUpload;
