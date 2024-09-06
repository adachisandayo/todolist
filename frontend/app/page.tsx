"use client";

import { useState, useEffect } from 'react';

// const API_BASE_URL ="http://192.168.0.18:5000";
const API_BASE_URL ="http://localhost:8000";


function Test(props) {
  const [char, setChar] = useState('');
  return (
    <div>
    <input
    type="text"
    value={char}
    onChange={(e) => setChar(e.target.value)}
    />
    <h1>{char}</h1>
    <h1>{props.x}</h1>
    </div>
  )
}

function ShowData(props) {
  const [changeItem, setChangeItem] = useState([]);
  const [selectedValue, setSelectedValue] = useState<string>('');

  // セレクトボックスの値が変更された時のハンドラー
  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedValue(event.target.value);
  };
  
  return(
    <div>
      <li> 
        {/* アイテムの表示 */}
        {props.item.id}
        &nbsp;&nbsp;&nbsp;
        {props.item.name}
        &nbsp;&nbsp;&nbsp;
        {props.item.categories}
        <br />
        {/* 内容の変更 */}
        <input
        type="text"
        value={changeItem}
        onChange={(e) => setChangeItem(e.target.value)}
        />
        <button onClick={() => {props.putItem(props.item.id, changeItem); 
                                setChangeItem('');}
                        }>Change</button>
         &nbsp;&nbsp;&nbsp;
        {/* 内容の削除 */}
        <button onClick={() => props.deleteItem(props.item.id)}>Delete</button>
        
        &nbsp;&nbsp;&nbsp;
        {/* タグの追加 */}
        <select id="dropdown" value={selectedValue} onChange={handleChange}>
        <option value="" disabled>tag</option>
        {Object.keys(props.categories).map(id => (
          <option key={id} value={id}>
            {props.categories[id]}
          </option>
        ))}
        </select>
        <button onClick={() => props.addItemCategory(props.item.id, selectedValue)}>add tag</button>
      </li>

    </div>
  )
}

function KariData(props) {
  const [changeItem, setChangeItem] = useState([]);
  const [selectedValue, setSelectedValue] = useState<string>('');

  // セレクトボックスの値が変更された時のハンドラー
  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedValue(event.target.value);
  };
  
  return(
    <div>
      <li> 
        {/* アイテムの表示 */}
        {props.item}
        {props.id}
        <br />
        {/* 内容の変更 */}
        <input
        type="text"
        value={changeItem}
        onChange={(e) => setChangeItem(e.target.value)}
        />
        <button onClick={() => {props.putItem(props.id, changeItem); 
                                setChangeItem('');}
                        }>Change</button>
         &nbsp;&nbsp;&nbsp;
        {/* 内容の削除 */}
        <button onClick={() => props.deleteItem(props.id)}>Delete</button>
      
      </li>

    </div>
  )
}

export default function Home() {
  const [items, setItems] = useState([]);
  const [newItem, setNewItem] = useState('');
  const [categories, setCategories] = useState([]);
  const [newCategory, setNewCategory] = useState('');

  useEffect(() => {
    fetchItems();
    fetchCategories();
  }, []);

  const fetchItems = async () => {
    const res = await fetch(`${API_BASE_URL}/items`);
    const data = await res.json();
    setItems(data);
  };

  const addItem = async () => {
    if (!newItem) return;
    const res = await fetch(`${API_BASE_URL}/items`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name: newItem }),
    });
    const data = await res.json();
    fetchItems();
    setNewItem('');
  };

  const deleteItem = async (id) => {
    const res = await fetch(`${API_BASE_URL}/items/${id}`, {
      method: 'DELETE',
    });
    const data = await res.json();
    fetchItems();
  };

  const putItem = async (id, changeItem) => {
    if (!changeItem) return;
    const res = await fetch(`${API_BASE_URL}/items/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name: changeItem}),
    });
    const data = await res.json();
    fetchItems();
  };


  const fetchCategories = async () => {
    const res = await fetch(`${API_BASE_URL}/categories`);
    const data = await res.json();
    setCategories(data);
  };

  const addCategory = async () => {
    if (!newCategory) return;
    const res = await fetch(`${API_BASE_URL}/categories`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name: newCategory }),
    });
    const data = await res.json();
    fetchCategories();
    setNewCategory('');
  }

  const deleteCategory = async (id) => {
    const res = await fetch(`${API_BASE_URL}/categories/${id}`, {
      method: 'DELETE',
    });
    const data = await res.json();
    fetchCategories();
  };

  const addItemCategory = async (itemid, categoryid) => {
    if (!categoryid) return;
    const res = await fetch(`${API_BASE_URL}/itemcategory`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ item_id:itemid, category_id:categoryid  }),
    })
    const data = await res.json();
    fetchItems();
    setNewItem('');
  }

  return (
    <div>
      <h1>Next.js + Flask + SQLite</h1>
      {/* todoリストの表示 */}
      <ul>
        {/* {Object.values(items).map((item, index) => (
          <ShowData 
            item={item}
            id = {item.id}
            categories={categories}
            putItem={putItem}
            deleteItem={deleteItem}
            addItemCategory={addItemCategory}
          />
          // <li>{item}</li>
        ))} */}
        {Object.keys(items).map(key => (
          <KariData
            item={items[key]}
            id = {key}
            putItem={putItem}
            deleteItem={deleteItem}
          />
        ))}
      </ul>
      {/* 内容の追加 */}
      <input
        type="text"
        value={newItem}
        onChange={(e) => setNewItem(e.target.value)}
      />
      <button onClick={addItem}>Add Item</button>
      {/* タグのリスト */}
      <h1>Tag list</h1>
      <ul>
        {Object.keys(categories).map((key, index) => (
          <li>
            {key}
            {categories[key]}
            &nbsp;&nbsp;&nbsp;
            <button onClick={() => deleteCategory(key)}>Delete</button>
          </li>
        ))}
      </ul>
      {/* タグの追加 */}
      <input
        type="text"
        value={newCategory}
        onChange={(e) => setNewCategory(e.target.value)}
      />
      <button onClick={addCategory}>Add Tag list</button>
  
      {/* <select id="dropdown" value={selectedValue} onChange={handleChange}>
        <option value="" disabled>Select an option</option>
        {Object.keys(categories).map( key => (
          <option key={key} value={categories[key]}>
          {categories[key]}
        </option>
        ))}
      </select>
      <p>Selected Value: {selectedValue}</p> */}
    </div>
  );
}

