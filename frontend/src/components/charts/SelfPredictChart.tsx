import {
  CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis,
  YAxis,
} from "recharts";
import type { SelfPredictChartPoint } from "../../api/students";

export default function SelfPredictChart({ data }: { data: SelfPredictChartPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={240}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
        <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="predicted" name="예측" stroke="#2b6fff" connectNulls />
        <Line type="monotone" dataKey="actual" name="실제" stroke="#ef4444" connectNulls />
      </LineChart>
    </ResponsiveContainer>
  );
}
