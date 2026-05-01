import clsx from "clsx";
import { PropsWithChildren } from "react";

type Props = PropsWithChildren<{
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
  className?: string;
}>;

export const Card = ({ title, subtitle, action, className, children }: Props) => (
  <section
    className={clsx("glass rounded-xl p-5 shadow-lg shadow-black/20", className)}
  >
    {(title || action) && (
      <header className="flex items-start justify-between mb-4">
        <div>
          {title && <h3 className="text-base font-semibold text-slate-100">{title}</h3>}
          {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
        </div>
        {action}
      </header>
    )}
    {children}
  </section>
);
