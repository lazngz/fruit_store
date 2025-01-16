import React from 'react';
import Login from './components/Login';
import ProductList from './components/ProductList';
import OrderHistory from './components/OrderHistory';

function App() {
    return (
        <div>
            <h1>Fruit Store</h1>
            <Login />
            <ProductList />
            <OrderHistory />
        </div>
    );
}

export default App;
