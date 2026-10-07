export default function DoctorDashboard() {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  return <div className="p-6 text-2xl font-bold">Doctor Dashboard: Dr. {user.name}</div>
}