export default function Button({
  variant = "primary",
  size = "md",
  as: Component = "button",
  className = "",
  ...props
}) {
  const classes = ["btn", `btn-${variant}`, `btn-${size}`, className].filter(Boolean).join(" ");
  return <Component className={classes} {...props} />;
}
