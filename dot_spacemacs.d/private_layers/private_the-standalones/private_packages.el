;; 'The standalones' is a layer that allow me to add standalone packages if needed :)

(setq the-standalones-packages
      '(
        pretty-mode
        ))

(defun the-standalones/init-pretty-mode ()
  (use-package pretty-mode))
