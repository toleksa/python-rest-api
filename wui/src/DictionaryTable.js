import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://192.168.0.136:5000';

function DictionaryTable() {
  const [data, setData] = useState([]);

  useEffect(() => {
    // TODO: request is sent twice on refresh
    axios.get(`${API_URL}/data`)
      .then(response => setData(response.data))
  }, []);

  const delEntryFn = async (delEntry) => {
    try {
      console.log(delEntry)
      await axios.delete(`${API_URL}/data/del/${delEntry}`);
    } catch (error) {
      console.error(error);
    }
  }

  return (
    <table className="table">
      <thead>
        <tr>
          <th>Key</th>
          <th>Value</th>
        </tr>
      </thead>
      <tbody>
        {data.map(entry => (
          <tr key={entry[0]}>
            <td>{entry[0]}</td>
            <td>{entry[1]}</td>
            <td><button className="btn btn-danger" onClick={() => delEntryFn(entry[0])}>Del</button></td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default DictionaryTable;
