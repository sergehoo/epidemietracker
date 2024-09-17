// src/components/UploaderComponent.jsx
import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button, Typography, Box, Grid, Paper } from '@mui/material';
import * as XLSX from 'xlsx';

const UploaderComponent = () => {
  const [files, setFiles] = useState([]);
  const [parsedData, setParsedData] = useState([]);
  const [columns, setColumns] = useState([]);

  // Handler for when files are dropped
  const onDrop = (acceptedFiles) => {
    setFiles(acceptedFiles);

    // Read the first file
    const file = acceptedFiles[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      const data = new Uint8Array(e.target.result);
      const workbook = XLSX.read(data, { type: 'array' });

      // Read the first sheet
      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];

      // Convert sheet to JSON
      const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

      // Set columns and data
      setColumns(jsonData[0] || []); // Set the first row as headers
      setParsedData(jsonData.slice(1)); // The rest as data
    };
    reader.readAsArrayBuffer(file);
  };

  // Dropzone setup
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: '.csv, .xlsx, .xls',
  });

  // Function to render preview of the parsed data
  const renderPreview = () => (
    <Paper sx={{ padding: 2, marginTop: 2 }}>
      <Typography variant="h6">Preview Data</Typography>
      <Box sx={{ overflowX: 'auto', maxHeight: 300 }}>
        <table >
          <thead>
            <tr>
              {columns.map((col, index) => (
                <th key={index}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {parsedData.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {row.map((cell, cellIndex) => (
                  <td key={cellIndex}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </Box>
    </Paper>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Uploader de Fichiers
      </Typography>
      <Box
        {...getRootProps()}
        sx={{
          border: '2px dashed #aaa',
          padding: '20px',
          textAlign: 'center',
          backgroundColor: isDragActive ? '#f0f8ff' : '#fafafa',
          cursor: 'pointer',
        }}
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <Typography>Déposez le fichier ici ...</Typography>
        ) : (
          <Typography>
            Glissez et déposez un fichier ici, ou cliquez pour sélectionner un fichier
          </Typography>
        )}
      </Box>

      {files.length > 0 && (
        <Grid container spacing={2} sx={{ marginTop: 2 }}>
          {files.map((file, index) => (
            <Grid item key={index} xs={12}>
              <Paper sx={{ padding: 2 }}>
                <Typography>
                  Fichier: {file.name} ({Math.round(file.size / 1024)} KB)
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      )}

      {parsedData.length > 0 && renderPreview()}

      {parsedData.length > 0 && (
        <Button
          variant="contained"
          color="primary"
          sx={{ marginTop: 2 }}
          onClick={() => {
            // Logic to map and validate data can go here
            alert('Importer les données validées');
          }}
        >
          Importer les Données
        </Button>
      )}
    </Box>
  );
};

export default UploaderComponent;