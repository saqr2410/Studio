import React from 'react'

const StatsCard = ({ title, value, icon, color }) => {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className={`w-12 h-12 ${color} rounded-full flex items-center justify-center text-white text-2xl`}>
          {icon}
        </div>
      </div>
    </div>
  )
}

export default StatsCard  // ✅ تأكد من هذا السطر