import React, { useState } from 'react'
import Options from './Options';

import axios from 'axios';
 

function FileUpload(){
    const [selectedFile, setSelectedFile] = useState(null);
    const [tableData, setTableData] = useState([]);


  const handleInputChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const submit = (event) => {
    event.preventDefault();
    const data = new FormData();
    data.append('file', selectedFile);
    data.append('filename','data.csv');
    let url = "/upload";

    axios.post(url, data)
      .then(res => {
        console.log(res.data);
        setTableData(JSON.parse(res.data));
        document.getElementById('message').innerHTML='Uploaded Succesfully!!';
      }).catch(error => {
        document.getElementById('message').innerHTML='ERROR!';
        // Handle the error here (e.g., show an error message to the user)
      });

  };

  return (
    <div>
      <form onSubmit={submit}>
        <input type="file" name="file" onChange={handleInputChange} />
        <input type="submit" value="Upload" />
        <p id='p'></p>
      </form>
      <Options rows={tableData} />
    </div>
  );
    
    
}

export default FileUpload;