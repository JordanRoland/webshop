import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Button, Input, Select } from "@/components/ui";
import axios from "axios";

export default function OrderHistoryPage() {
  const [orders, setOrders] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem("user"));
    axios.get("http://localhost:5000/orders", {
      headers: { Authorization: `Bearer ${user.token}` }
    }).then((response) => {
      setOrders(response.data);
    }).catch(() => {
      setError("Hiba történt a rendelések lekérdezése során!");
    });
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <motion.div 
        initial={{ opacity: 0, y: -20 }} 
        animate={{ opacity: 1, y: 0 }}
        className="bg-white p-8 rounded-2xl shadow-lg w-96"
      >
        <h2 className="text-2xl font-bold mb-4">Korábbi rendeléseim</h2>
        {error && <p className="text-red-500 text-sm">{error}</p>}
        <div className="space-y-4">
          {orders.length === 0 ? (
            <p className="text-gray-500">Nincsenek korábbi rendelései.</p>
          ) : (
            orders.map((order, index) => (
              <div key={index} className="p-4 border rounded-lg bg-gray-50">
                <p><strong>Termék:</strong> {order.product}</p>
                <p><strong>Mennyiség:</strong> {order.quantity} kg</p>
                <p><strong>Kiszállítási dátum:</strong> {order.delivery_date}</p>
                {order.note && <p><strong>Megjegyzés:</strong> {order.note}</p>}
                <p className="text-sm text-gray-500">Rögzítve: {order.created_at}</p>
              </div>
            ))
          )}
        </div>
      </motion.div>
    </div>
  );
}
