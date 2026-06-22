import { Badge } from '@/components/ui/badge';
import { getStatusVariant } from '@/lib/ui/statusVariants';

interface Props {
  value: string;
  label?: string;
}

export function StatusBadge({ value, label }: Props) {
  return <Badge variant={getStatusVariant(value)}>{label ?? value}</Badge>;
}
