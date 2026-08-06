import {
  PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart,
  ResponsiveContainer,
} from "recharts";
import type { PrismScore } from "../../api/students";

export default function PrismRadarChart({ score }: { score: PrismScore }) {
  const data = [
    { axis: "P 계산정확성", value: score.score_p },
    { axis: "R 조건해석", value: score.score_r },
    { axis: "I 개념내재", value: score.score_i },
    { axis: "S 전략선택", value: score.score_s },
    { axis: "M 시간관리", value: score.score_m },
  ];

  return (
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart data={data} outerRadius="75%">
        <PolarGrid />
        <PolarAngleAxis dataKey="axis" tick={{ fontSize: 11 }} />
        <PolarRadiusAxis domain={[0, 5]} tickCount={6} tick={{ fontSize: 10 }} />
        <Radar dataKey="value" stroke="#4F46E5" fill="#4F46E5" fillOpacity={0.25} />
      </RadarChart>
    </ResponsiveContainer>
  );
}
