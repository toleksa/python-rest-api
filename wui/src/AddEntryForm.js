import React, { useState } from 'react';
import axios from 'axios';

function AddEntryForm() {
  const [key, setKey] = useState('');
  const [value, setValue] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://192.168.0.136:5000/data/add', { [key]: value });
      setKey('');
      setValue('');
    } catch (error) {
      console.error(error);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="keyInput">Key</label>
        <input type="text" className="form-control" id="keyInput" value={key} onChange={e => setKey(e.target.value)} />
      </div>
      <div className="form-group">
        <label htmlFor="valueInput">Value</label>
        <input type="text" className="form-control" id="valueInput" value={value} onChange={e => setValue(e.target.value)} />
      </div>
      <button type="submit" className="btn btn-primary">Submit</button>
    </form>
  );
}

export default AddEntryForm;
