import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import api from '../api'

export default function Register() {
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'patient' })
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    try {
      await api.post('/auth/register', form)
      navigate('/login')
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form onSubmit={submit} className="bg-white p-8 rounded-xl shadow w-96 space-y-4">
        <h1 className="text-2xl font-bold">Register</h1>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <select className="w-full border p-2 rounded" value={form.role} onChange={set('role')}>
          <option value="patient">Patient</option>
          <option value="doctor">Doctor</option>
        </select>
        <input className="w-full border p-2 rounded" placeholder="Full name" onChange={set('name')} required />
        <input className="w-full border p-2 rounded" placeholder="Email" type="email" onChange={set('email')} required />
        <input className="w-full border p-2 rounded" placeholder="Password (8+ chars)" type="password" onChange={set('password')} required />
        <button className="w-full bg-blue-600 text-white p-2 rounded">Create Account</button>
        <p className="text-sm">Have an account? <Link className="text-blue-600" to="/login">Sign in</Link></p>
      </form>
    </div>
  )
}