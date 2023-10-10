import React, { useState, useEffect } from 'react';
import Table from './Table';

import axios from 'axios';


const Options = ({ rows }) => {
  const [columnValues, setColumnValues] = useState([]);
  const [latestRows, setLatestRows] = useState(rows);
  const [reportHtml, setReportHtml] = useState('');


  useEffect(() => {
    if (rows.length > 0) {
      const keys = Object.keys(rows[0]);
      setColumnValues(keys);
      setLatestRows(rows);
    }
  }, [rows]);

  const initialItem = {
    colVal: '',
    option1: '',
    option2: '',
    option3: '',
  };

  const Dropdown = ({ options, value, onChange }) => (
    <select value={value} onChange={onChange}>
      <option value="">Select an option</option>
      {options.map((option) => (
        <option key={option} value={option}>
          {option}
        </option>
      ))}
    </select>
  );

  const options = {
    colVal: columnValues,
    option1: ['Missing', 'Normalization', 'Statistics','Encoding','Remove Column'],
    option2: {
      'Missing': ['Delete', 'NAN', 'Mean', 'Median','Fill with..'],
      'Normalization': ['Min-Max Scaling', 'Z-Score', 'Robust Scaling'],
      'Encoding':['Label Encoding','One Hot Encoding'],
      'Remove Column':[]
    },
  };

  const [items, setItems] = useState([{ ...initialItem }]);
  const [jsonData, setJsonData] = useState({});

  const handleDropdownChange = (index, optionKey, value) => {
    const newItems = [...items];
    newItems[index][optionKey] = value;
    setItems(newItems);
  };



  const handleAddItem = () => {
    setItems((prevItems) => [...prevItems, { ...initialItem }]);
  };


  const handleSendData = () => {
    const formattedData = items.map((item, index) => {
      // acc[`item${index + 1}`] = item;
      return item;
    }, {});

    setJsonData(formattedData);
    // You can now send jsonData to the server
    let url = "/get_items";
    axios.post(url, formattedData)
      .then(res => {
        console.log(res.data);
        // setLatestRows(JSON.parse(res.data));
        setLatestRows(res.data);
        document.getElementById('message').innerHTML='Successful!';
      })
      .catch(error => {
        document.getElementById('message').innerHTML='ERROR!';
        // Handle the error here (e.g., show an error message to the user)
      });
  };


  const handleSummaryReport = () => {
    

    // You can now send jsonData to the server

    

    axios.get('/get_summary')
      .then(response => {
        // console.log(res.data);
        // // setLatestRows(JSON.parse(res.data));
        // setLatestRows(res.data);
        // Create a URL for the blob data and trigger a download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'report.html');
      document.body.appendChild(link);
      link.click();

      // Clean up
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
        document.getElementById('message').innerHTML='Successful!';
      })
      .catch(error => {
        document.getElementById('message').innerHTML='ERROR!';
        // Handle the error here (e.g., show an error message to the user)
      });


    // let url = "/get_summary";
    // axios.get(url)
    //   .then(res => {
    //     // console.log(res.data);
    //     // setLatestRows(JSON.parse(res.data));
    //     setReportHtml(res.data.report_path);

    //     document.getElementById('message').innerHTML=res.data.report_path;
    //   })
    //   .catch(error => {
    //     document.getElementById('message').innerHTML=error;
    //     // Handle the error here (e.g., show an error message to the user)
    //   });
  };

  const handleRemoveItem = (indexToRemove) => {
    setItems((prevItems) => prevItems.filter((item, index) => index !== indexToRemove));
  };

  const handleRemoveXTrain = (indexToRemove) => {
    setXTrains((prevItems) => prevItems.filter((item, index) => index !== indexToRemove));
  };

  const handleRemoveYTrain = (indexToRemove) => {
    setYTrains((prevItems) => prevItems.filter((item, index) => index !== indexToRemove));
  };

  const handleDownload =() => {
    const formattedData = items.map((item, index) => {
      // acc[`item${index + 1}`] = item;
      return item;
    }, {});

    setJsonData(formattedData);
    axios.post('/preprocess_data', formattedData)
      .then(response => {
        // console.log(res.data);
        // // setLatestRows(JSON.parse(res.data));
        // setLatestRows(res.data);
        // Create a URL for the blob data and trigger a download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'data.csv');
      document.body.appendChild(link);
      link.click();

      // Clean up
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
        document.getElementById('message').innerHTML='Successful!';
      })
      .catch(error => {
        document.getElementById('message').innerHTML='ERROR!';
        // Handle the error here (e.g., show an error message to the user)
      });

    

      
    
  };


  
  const downloadTrainedModel = () => {
    

    // You can now send jsonData to the server

    

    axios.get('/download_model')
      .then(response => {
        // console.log(res.data);
        // // setLatestRows(JSON.parse(res.data));
        // setLatestRows(res.data);
        // Create a URL for the blob data and trigger a download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'model.pkl');
      document.body.appendChild(link);
      link.click();

      // Clean up
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
        document.getElementById('message').innerHTML='Successful!';
      })
      .catch(error => {
        document.getElementById('message').innerHTML='ERROR!';
        // Handle the error here (e.g., show an error message to the user)
      });

  };

  const [XTrains, setXTrains] = useState([[]]);
  const [yTrains, setYTrains] = useState([[]]);
  const [selectedOptions, setSelectedOptions] = useState([]);


  const addXTrains = () => {
    setXTrains([...XTrains, []]);
  };

  const addYTrain = () => {
    setYTrains([...yTrains, []]);
  };

  const handleXTrainChange = (index, option) => {
    const updatedDropdowns = [...XTrains];
    updatedDropdowns[index] = option;
    setXTrains(updatedDropdowns);
  };

  const handleYTrainChange = (index, option) => {
    const updatedDropdowns = [...yTrains];
    updatedDropdowns[index] = option;
    setYTrains(updatedDropdowns);
  };

  const handleSendClick = () => {
    const selectedXTrains = XTrains
      .map((dropdown) => dropdown || null) // Replace empty dropdowns with null
      .filter((option) => option !== null);
      const preprocessCommands = items.map((item, index) => {
        // acc[`item${index + 1}`] = item;
        return item;
      }, {});
      const selectedYTrain = yTrains
      .map((dropdown) => dropdown || null) // Replace empty dropdowns with null
      .filter((option) => option !== null);
      
    const jsonResult = {
      preprocessCommands,
      selectedXTrains,
      selectedYTrain,
      selectedAlgorithm,
      parameterValue
    };
    setJsonData(jsonResult);
    console.log(jsonResult); // You can do whatever you want with the JSON object

    let url = "/train_data";
    axios.post(url, jsonResult)
      .then(res => {
        console.log(res.data);
        // setLatestRows(JSON.parse(res.data));
        // setLatestRows(res.data);
        document.getElementById('message').innerHTML='Successful';
      })
      .catch(error => {
        document.getElementById('message').innerHTML='ERROR!';
        // Handle the error here (e.g., show an error message to the user)
      });

    // Reset the selected options and dropdowns
    setSelectedOptions([]);
    setXTrains([[]]);
  };


  const [selectedAlgorithm, setSelectedAlgorithm] = useState('');
  const [parameterValue, setParameterValue] = useState('');

  const handleAlgorithmChange = (e) => {
    setSelectedAlgorithm(e.target.value);
  };

  const handleParameterChange = (e) => {
    setParameterValue(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // You can handle the selected algorithm and parameter value here
    console.log('Selected Algorithm:', selectedAlgorithm);
    console.log('Parameter Value:', parameterValue);
  };

  return (
    <div>
    <form>
      
      <div>
        {items.map((item, index) => (
          <div key={index}>
            <Dropdown
              options={options.colVal}
              value={item.colVal}
              onChange={(e) => handleDropdownChange(index, 'colVal', e.target.value)}
              
            />
            {item.colVal && (
              <Dropdown
                options={options.option1}
                value={item.option1}
                onChange={(e) => handleDropdownChange(index, 'option1', e.target.value)}
              />
            )}

            {item.option1 && options.option2[item.option1] && (
              <Dropdown
                options={options.option2[item.option1]}
                value={item.option2}
                onChange={(e) => handleDropdownChange(index, 'option2', e.target.value)}
              />
            )}
            <button type="button" onClick={() => handleRemoveItem(index)}>Remove Item</button>
          </div>
        ))}
        <button type="button" onClick={handleAddItem}>Add Item</button>
        <button type="button" onClick={handleSendData}>Send Data</button>
        
        <pre>{JSON.stringify(jsonData, null, 2)}</pre>
        <p id='message'></p>
      </div>
      <button type="button" onClick={handleDownload}>
        Download CSV
      </button>

      <button type="button" onClick={handleSummaryReport}>
        Generate Summary
      </button>
      
      
    </form>

    <button onClick={addXTrains}>Add Dropdown</button>

      {XTrains.map((dropdown, index) => (
        <div key={index}>
          <select
            value={dropdown}
            onChange={(e) => handleXTrainChange(index, e.target.value)}
          >
            <option value="">Select an option</option>
            {options.colVal.map((option, optionIndex) => (
              <option key={optionIndex} value={option}>
                {option}
              </option>
              
            ))}
          </select>
          <button type="button" onClick={() => handleRemoveXTrain(index)}>Remove Item</button>
        </div>
      ))}


<button onClick={addYTrain}>Add Dropdown</button>
    {yTrains.map((dropdown, index) => (
            <div key={index}>
              <select
                value={dropdown}
                onChange={(e) => handleYTrainChange(index, e.target.value)}
              >
                <option value="">Select an option</option>
                {options.colVal.map((option, optionIndex) => (
                  <option key={optionIndex} value={option}>
                    {option}
                  </option>
                ))}
              </select>
              <button type="button" onClick={() => handleRemoveYTrain(index)}>Remove Item</button>
            </div>
          ))}

      <h3>Choose Algorithm</h3>
      <label>
        Algorithm:
        <select value={selectedAlgorithm} onChange={handleAlgorithmChange}>
          <option value="">Select an algorithm</option>
          <option value="LogisticRegression">Logistic Regression</option>
          <option value="DecisionTree">Decision Tree</option>
          <option value="RandomForest">Random Forest</option>
          <option value="SVM">SVM</option>
          {/* Add more algorithm options here */}
        </select>
      </label>

      {selectedAlgorithm && (
        <div>
          <label>
            Parameter Value:
            <input
              type="text"
              value={parameterValue}
              onChange={handleParameterChange}
            />
          </label>
        </div>
      )}

 
      <button onClick={handleSendClick}>Send</button>
      
      <button onClick={downloadTrainedModel}>Download Trained Model</button>

      
    
    <Table rows={latestRows} />

    {/* <iframe src="https://www.youtube.com/" width="100%" height="800" title="Pandas Profiling Report"></iframe> */}

    </div>
    
  );
};


export default Options;
