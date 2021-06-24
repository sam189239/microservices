import React, { useEffect } from 'react';
import Wrapper from "./Wrapper"
import {Product} from "../interfaces/product"
import {Link} from "react-router-dom";
import * as Constants from '../constants'

const Products = () => {
    const [products, setProducts] = React.useState([]);
    useEffect(() => {
        (
            async () => {
                const response = await fetch('http://'+Constants.adminhost+':8000/api/products');

                const data =await response.json();

                console.log(data)
                setProducts(data);
            }
        )();
    }, []);
    
    const del = async (id: number) =>{
        if(window.confirm("Are you sure you want to delete this product?")){
            await fetch('http://'+Constants.adminhost+`:8000/api/products/${id}`,{
                method: 'DELETE'
            });
            setProducts(products.filter((p: Product) => p.id!=id));
        }
    }

    const create_user = async () =>{
        if(window.confirm("Are you sure you want to create User?")){
            await fetch('http://'+Constants.adminhost+':8000/api/user',{
                method: 'POST'
            });
        }
    }
    return(
        <Wrapper>
            <div className="pt-3 pb-2 mb-3 border-bottom">
                <div className="btn-toolbar mb-2 mb-md-0">
                    <Link to='/admin/products/create' className="btn btn-sm btn-outline-secondary">Add Product</Link>
                    <a href="#" className="btn btn-sm btn-outline-secondary" onClick={() => create_user()}>Add User</a>
                </div>
            </div>
            <div className="table-responsive">
                <table className="table table-striped table-sm">
                    <thead>
                    <tr>
                        <th>#</th>
                        <th>Image</th>
                        <th>Title</th>
                        <th>Likes</th>
                        <th>Action</th>
                    </tr>
                    </thead>
                    <tbody>
                    {products.map(
                        (p:Product) => {
                        return(
                            <tr key={p.id}>
                                <td>{p.id}</td>
                                <td><img src={p.image} height="180"/></td>
                                <td>{p.title}</td>
                                <td>{p.likes}</td>
                                <td>
                                    <div className="btn-group mr-2">
                                        <Link to={`/admin/products/${p.id}/edit`} 
                                            className="btn btn-sm btn-outline-secondary">Edit</Link>
                                        <a href="#" className="btn btn-sm btn-outline-secondary" 
                                            onClick={() => del(p.id)}>Delete</a>
                                    </div>
                                </td>
                            </tr>  
                        )
                    })}
                    
                    </tbody>
                </table>
            </div>
        </Wrapper>
    );
};

export default Products;
