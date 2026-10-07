import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import api from '../api'

const METRICS = ['heart_rate', 'steps', 'sleep_hours', 'spo2']

export default function PatientDashboard() {
  const [metric, setMetric] = useState('heart_rate')
  const [days, setDays] = useState(7)
  const [data, setData] = useState([])
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  useEffect(() => {
    api.get('/health/measurements', { params: { metric, days } }).then((res) =>
      setData(res.data.map((m) => ({
        time: new Date(m.recorded_at).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit' }),
        value: m.value,
      })))
    )
  }, [metric, days])

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Welcome, {user.name}</h1>
      <div className="flex gap-2 mb-4">
        {METRICS.map((m) => (
          <button key={m} onClick={() => setMetric(m)}
            className={`px-3 py-1 rounded ${metric === m ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
            {m.replace('_', ' ')}
          </button>
        ))}
        <select className="ml-auto border rounded px-2" value={days} onChange={(e) => setDays(+e.target.value)}>
          <option value={1}>Day</option><option value={7}>Week</option><option value={30}>Month</option>
        </select>
      </div>
      <div className="bg-white rounded-xl shadow p-4 h-80">
        <ResponsiveContainer>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" /><YAxis /><Tooltip />
            <Line type="monotone" dataKey="value" stroke="#2563eb" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}