import os

path_styles = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\styles.scss"
with open(path_styles, "r", encoding="utf-8") as f:
    content = f.read()

responsive_additions = """
/* ==========================================================================
   UI / UX PRO MAX — RESPONSIVE TABLES & ACCESSIBLE PATTERNS
   ========================================================================== */

.table-responsive {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  margin-bottom: 0.5rem;
  position: relative;

  /* Touch scrolling smooth */
  scroll-behavior: smooth;

  /* Discreet scrollbar */
  &::-webkit-scrollbar {
    height: 6px;
    width: 6px;
  }
  &::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 4px;
  }
  &::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 4px;
    &:hover {
      background: #94a3b8;
    }
  }
}

/* Accessible focus ring */
:focus-visible {
  outline: 2px solid var(--primary-teal);
  outline-offset: 2px;
}

/* Touch targets >= 44x44px for accessibility */
button, a.btn, input, select {
  min-height: 40px;
}

/* Badges for status and medical units */
.badge-bed {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.6rem;
  border-radius: var(--radius-sm);
  background: #f0fdfa;
  color: #0f766e;
  border: 1px solid #ccfbf1;
  font-weight: 700;
  font-size: 0.78rem;
}

.patient-cell-wrapper, .doctor-cell-wrapper, .bed-cell-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 130px;
}

/* Global Table Typography and Spacing */
.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;

  th, td {
    vertical-align: middle;
  }
}

/* Responsive Grid Utility Helpers */
@media (max-width: 768px) {
  .responsive-stack-sm {
    flex-direction: column !important;
    align-items: stretch !important;
  }
  .hide-on-mobile {
    display: none !important;
  }
}
"""

if ".table-responsive" not in content:
    content += "\n" + responsive_additions
    with open(path_styles, "w", encoding="utf-8") as f:
        f.write(content)
    print("styles.scss updated with responsive rules.")
else:
    print("styles.scss already contains .table-responsive.")

