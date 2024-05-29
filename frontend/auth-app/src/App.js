import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Login from './Login'
import Protected from './Protected'

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path='/' element={<Login/>}/>
        <Route path='/protected' element={<Protected/>}/>
      </Routes>
    </Router>
  )
}

export default App