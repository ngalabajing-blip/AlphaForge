type Props = {
  title: string;
  description?: string;
  icon?: string;
  action?: React.ReactNode;
};

export const EmptyState = ({ title, description, icon, action }: Props) => (
  <div className="flex flex-col items-center justify-center text-center py-16 text-slate-400">
    <div className="text-3xl mb-3">{icon || "✨"}</div>
    <h4 className="text-base font-semibold text-slate-200">{title}</h4>
    {description && <p className="text-sm mt-1 max-w-md">{description}</p>}
    {action && <div className="mt-4">{action}</div>}
  </div>
);
