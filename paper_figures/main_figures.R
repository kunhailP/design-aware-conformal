#!/usr/bin/env Rscript
# Publication-graphics layer: main Figures 1-4.
# Python owns inference (results/*.csv); this file only draws.
# Rule: no on-page type below 7 pt; same meaning = same color in every figure.
suppressPackageStartupMessages({
  library(ggplot2); library(dplyr); library(tidyr); library(readr)
  library(cowplot); library(ggrepel); library(scales); library(scico)
  library(sf); library(jsonlite)
})

NAVY <- "#2B4C7E"; TEAL <- "#3A7D78"; RUST <- "#B45F47"
AMBER <- "#C89B4B"; GRAYN <- "#777A7D"; GRID <- "#E5E5E5"
SEQ5 <- c("#DDDBD3", "#B9C7CE", "#7FA3B5", "#41758F", NAVY)

thm <- function(base = 8.5) theme_minimal(base_size = base) +
  theme(panel.grid.minor = element_blank(),
        panel.grid.major = element_line(color = GRID, size = 0.3),
        axis.title = element_text(size = 8.5, color = "#222222"),
        axis.text = element_text(size = 7.5, color = "#555555"),
        plot.title = element_text(size = 9.5, face = "bold",
                                  color = "#222222", hjust = 0),
        legend.text = element_text(size = 7.2),
        legend.title = element_text(size = 7.6),
        plot.background = element_rect(fill = "white", color = NA))

lb <- function(x) as.logical(x == "True" | x == TRUE)

## ---------------------------------------------------------------- Figure 1
fig1 <- function() {
  # A. schematic
  set.seed(3); L <- 4; T <- 5
  base <- seq(.25, .75, length.out = T)
  tr <- do.call(rbind, lapply(1:L, function(r)
    tibble(r = r, t = 1:T, x = seq(.1, .9, length.out = T),
           y = .84 - .19 * (r - 1) +
             .09 * (base + .05 * r + rnorm(T, 0, .02) -
                    mean(base + .05 * r)))))
  A <- ggplot(tr) +
    geom_line(aes(x, y, group = r), color = NAVY, size = .5) +
    annotate("text", x = .02, y = .84 - .19 * (0:3), hjust = 1, size = 2.6,
             color = GRAYN, label = paste0("r=", 1:4)) +
    annotate("rect", xmin = .295, xmax = .37, ymin = .18, ymax = .95,
             fill = NA, color = RUST, linetype = "dotted", size = .45) +
    annotate("text", x = .33, y = 1.00, label = "per threshold",
             color = RUST, size = 2.7, vjust = 0) +
    annotate("rect", xmin = .06, xmax = .95, ymin = .565, ymax = .755,
             fill = NA, color = GRAYN, linetype = "dashed", size = .45) +
    annotate("text", x = .965, y = .66, label = "per round", color = GRAYN,
             size = 2.7, hjust = 0) +
    annotate("rect", xmin = .035, xmax = 1.13, ymin = .13, ymax = 1.0,
             fill = NA, color = TEAL, size = .65) +
    annotate("text", x = .58, y = .065,
             label = "the~claim:~whole~'{'*F[c*','*r](t)*'}'[r*','*t]",
             parse = TRUE, color = TEAL, size = 3.0) +
    coord_cartesian(xlim = c(-.12, 1.2), ylim = c(0, 1.06), expand = FALSE) +
    theme_void() + ggtitle("A.  The unit mismatch") +
    theme(plot.title = element_text(size = 9.5, face = "bold", hjust = 0))
  # B. landscape
  land <- read_csv("results/wrong_unit_landscape.csv", show_col_types = FALSE)
  m <- filter(land, method == "marginal")
  B <- ggplot(m, aes(L, dep)) +
    geom_raster(aes(fill = traj_cov_pct)) +
    geom_contour(aes(z = traj_cov_pct), breaks = c(5, 15, 30),
                 color = "white", size = .35) +
    annotate("text", x = c(2.9, 4.6, 7.2), y = c(.84, .74, .60),
             label = c("30%", "15%", "5%"), color = "white", size = 2.6) +
    scale_fill_scico(palette = "batlow", limits = c(0, 90),
                     name = "coverage %") +
    scale_x_continuous(breaks = c(2, 4, 6, 8, 10), expand = c(0, 0)) +
    scale_y_continuous(breaks = c(0, .3, .6, .9), expand = c(0, 0)) +
    labs(x = "trajectory length L", y = "round-to-round dependence",
         title = "B.  Wrong-unit collapse surface") +
    thm() + theme(legend.key.height = unit(.55, "cm"),
                  legend.key.width = unit(.28, "cm"))
  # C. slices
  d <- read_csv("results/wrong_unit_coverage.csv", show_col_types = FALSE) |>
    mutate(method = recode(method, marginal = "per threshold",
                           per_round = "per round",
                           trajectory = "trajectory"))
  bench <- tibble(L = seq(2, 8, .5), y = 100 * .9^L)
  lastp <- d |> group_by(method) |> slice_max(L, n = 1)
  C <- ggplot(d, aes(L, traj_cov_pct, color = method)) +
    geom_hline(yintercept = 90, color = NAVY, linetype = "dashed",
               size = .4) +
    geom_line(data = bench, aes(L, y), inherit.aes = FALSE, color = GRAYN,
              linetype = "dotdash", size = .4) +
    annotate("text", x = 3.4, y = 100 * .9^3.4 - 7,
             label = "0.9^L~benchmark", parse = TRUE,
             color = GRAYN, size = 2.6) +
    annotate("text", x = 2.1, y = 95, label = "nominal 90%", color = NAVY,
             size = 2.6, hjust = 0) +
    geom_line(size = .55) + geom_point(size = 1.4) +
    geom_text_repel(data = lastp, aes(label = sprintf("%s  %.1f", method,
                                                      traj_cov_pct)),
                    size = 2.7, direction = "y", nudge_x = 1.3,
                    segment.color = NA, show.legend = FALSE) +
    scale_color_manual(values = c(`trajectory` = TEAL, `per round` = GRAYN,
                                  `per threshold` = RUST), guide = "none") +
    scale_x_continuous(breaks = c(2, 4, 6, 8), limits = c(2, 11.6)) +
    scale_y_continuous(limits = c(0, 100)) +
    labs(x = "trajectory length L", y = "whole-trajectory coverage (%)",
         title = "C.  Slices at the benchmark") + thm()
  fig <- plot_grid(A, plot_grid(B, C, nrow = 1, rel_widths = c(1.25, 1)),
                   ncol = 1, rel_heights = c(.85, 1.45))
  ggsave("paper/figures/wrong_unit_coverage.pdf", fig, width = 5.5,
         height = 4.7, device = cairo_pdf, bg = "white")
  ggsave("paper/figures/wrong_unit_coverage.png", fig, width = 5.5,
         height = 4.7, dpi = 300, bg = "white")
}

## ---------------------------------------------------------------- Figure 2
fig2 <- function() {
  RHO0 <- .47; TAU <- (0.02 - 0.0061) / 0.0943; KST <- ceiling(1 + 2 / TAU^2)
  d <- read_csv("results/feasibility_frontier.csv", show_col_types = FALSE) |>
    mutate(activated = lb(activated),
           ds = recode(dataset,
                       `WVS full-coverage items` = "WVS items",
                       `ESS national-unit scan` = "ESS national",
                       `ESS small-area (e54)` = "ESS small-area",
                       `ESS small-area, common NUTS level` =
                         "small-area, one NUTS level"))
  surf <- expand.grid(K = exp(seq(log(8), log(420), length.out = 60)),
                      rho = seq(0, .62, length.out = 120)) |>
    mutate(G = 1 - sqrt(1 - rho^2))
  glines <- tibble(g = c(.02, .05, .10, .20)) |>
    mutate(rho = sqrt(1 - (1 - g)^2),
           lab = paste0("cut ", 100 * g, "%"))
  A <- ggplot() +
    geom_raster(data = surf, aes(K, rho, fill = G), alpha = .30) +
    scale_fill_scico(palette = "batlow", guide = "none", begin = .15,
                     end = .70) +
    geom_hline(data = glines, aes(yintercept = rho), color = "white",
               size = .3) +
    geom_text(data = glines, aes(x = 400, y = rho + .012, label = lab),
              color = "grey25", size = 2.5, hjust = 1) +
    geom_hline(yintercept = RHO0, color = NAVY, linetype = "dashed",
               size = .5) +
    geom_vline(xintercept = KST, color = NAVY, linetype = "dashed",
               size = .5) +
    annotate("text", x = 8.6, y = RHO0 + .022, label = "need~gate~rho[0]",
             parse = TRUE, color = NAVY, size = 2.8, hjust = 0) +
    annotate("text", x = KST * 0.92, y = .335,
             label = "reliability~floor~K==1+2/tau[D]^2", parse = TRUE,
             color = NAVY, size = 2.6, hjust = 1, angle = 90) +
    annotate("text", x = 10, y = .60, label = "unlearnable", fontface = 3,
             color = "grey20", size = 3.0, hjust = 0) +
    annotate("text", x = 170, y = .60, label = "feasible", fontface = 3,
             color = "grey20", size = 3.0, hjust = 0) +
    annotate("text", x = 10, y = .095, label = "unnecessary", fontface = 3,
             color = "grey20", size = 3.0, hjust = 0) +
    geom_linerange(data = d, aes(x = K, ymin = rho_lcb, ymax = rho_hat,
                                 color = ds), size = .35, alpha = .6) +
    geom_point(data = filter(d, !activated),
               aes(K, rho_lcb, color = ds, shape = ds), size = 1.5,
               stroke = .6, fill = "white") +
    geom_point(data = filter(d, activated), aes(K, rho_lcb), shape = 21,
               size = 3.4, color = NAVY, fill = NA, stroke = .7) +
    geom_point(data = filter(d, activated), aes(K, rho_lcb, shape = ds),
               size = 1.7, color = TEAL) +
    scale_shape_manual(values = c(`WVS items` = 22, `ESS national` = 21,
                                  `ESS small-area` = 24,
                                  `small-area, one NUTS level` = 23),
                       name = NULL) +
    scale_color_manual(values = c(`WVS items` = AMBER,
                                  `ESS national` = RUST,
                                  `ESS small-area` = TEAL,
                                  `small-area, one NUTS level` = TEAL),
                       name = NULL) +
    scale_x_log10(limits = c(8, 420), expand = c(0, 0)) +
    scale_y_continuous(limits = c(0, .62), expand = c(0, 0)) +
    labs(x = "exchangeable populations K (log scale)",
         y = expression(hat(rho) ~ "(whisker: LCB to estimate)"),
         title = "A.  The feasibility frontier") +
    thm() +
    theme(legend.position = c(.52, .015), legend.justification = c(.5, 0),
          legend.key.size = unit(.32, "cm"),
          legend.background = element_blank())
  sa <- read_csv("results/small_area_transport.csv",
                 show_col_types = FALSE) |>
    filter(pool == "all countries", branch == "deconvolution") |>
    mutate(ratio = 1 - (gain_lcb + .05), cert = 1 - gain_lcb,
           lab = paste0("K=", K))
  B <- ggplot(sa, aes(y = reorder(lab, -K))) +
    geom_vline(xintercept = 1, color = RUST, linetype = "dashed",
               size = .45) +
    geom_segment(aes(x = ratio, xend = cert, yend = reorder(lab, -K)),
                 color = "grey55", size = .5) +
    geom_point(aes(x = cert), shape = 124, size = 3, color = "grey45") +
    geom_point(aes(x = ratio), shape = 17, size = 2.1, color = TEAL) +
    annotate("text", x = .985, y = 4.45, label = "conservative\nenvelope",
             color = RUST, size = 2.4, hjust = 1, vjust = 1) +
    scale_x_continuous(limits = c(.62, 1.08),
                       breaks = c(.7, .8, .9, 1.0)) +
    labs(x = "width vs conservative", y = NULL,
         title = "B.  What activation buys") +
    thm() + theme(panel.grid.major.y = element_blank())
  fig <- plot_grid(A, B, nrow = 1, rel_widths = c(2.62, 1.05))
  ggsave("paper/figures/feasibility_frontier.pdf", fig, width = 5.5,
         height = 3.9, device = cairo_pdf, bg = "white")
  ggsave("paper/figures/feasibility_frontier.png", fig, width = 5.5,
         height = 3.9, dpi = 300, bg = "white")
}

## ---------------------------------------------------------------- Figure 3
fig3 <- function() {
  cty <- read_csv("results/ess_country_certification.csv",
                  show_col_types = FALSE) |>
    filter(outcome == "trstprl") |>
    mutate(across(c(any_plugin, any_da, net_da, persist_da), lb))
  # A. Hasse
  nodes <- tibble(k = c("marginal", "any-pair", "net", "persistent"),
                  x = c(.5, .10, .90, .5), y = c(.06, .5, .5, .94),
                  da = c(sum(cty$any_plugin), sum(cty$any_da),
                         sum(cty$net_da), sum(cty$persist_da)))
  edges <- tibble(x = c(.5, .5, .10, .90), y = c(.10, .10, .545, .545),
                  xe = c(.135, .865, .465, .535), ye = c(.46, .46, .90, .90))
  A <- ggplot() +
    geom_segment(data = edges, aes(x, y, xend = xe, yend = ye),
                 color = "grey60", size = .5) +
    geom_point(data = nodes, aes(x, y), size = 17, shape = 21,
               fill = "white", color = NAVY, stroke = .8) +
    geom_text(data = nodes, aes(x, y + .045, label = k), size = 2.55,
              color = "#222222") +
    geom_text(data = nodes, aes(x, y - .035, label = da), size = 3.3,
              fontface = "bold", color = TEAL) +
    annotate("text", x = .5, y = .5, label = "no edge:\nincomparable",
             size = 2.5, color = GRAYN, fontface = 3) +
    coord_cartesian(xlim = c(-.08, 1.08), ylim = c(-.04, 1.08)) +
    theme_void() + ggtitle("A.  The claim family") +
    theme(plot.title = element_text(size = 9.5, face = "bold", hjust = 0))
  # C. SNR mechanism
  pair <- read_csv("results/ess_design_aware_decline.csv",
                   show_col_types = FALSE) |>
    filter(outcome == "trstprl", M0_plugin == 1) |>
    mutate(status = ifelse(M4_design == 1, "retained",
                           "reclassified inconclusive"))
  lim <- max(pair$design_sd) * 1.15
  iso <- tibble(k = c(1, 2, 4)) |>
    mutate(xe = pmin(lim, max(pair$signal) * 1.1 / k))
  C <- ggplot(pair, aes(design_sd, signal)) +
    geom_segment(data = iso, aes(x = 0, y = 0, xend = xe, yend = k * xe),
                 inherit.aes = FALSE, color = "grey75", size = .35,
                 linetype = c("dotted", "dashed", "solid")) +
    geom_text(data = iso, aes(x = xe, y = k * xe,
                              label = paste0("SNR ", k)),
              inherit.aes = FALSE, size = 2.5, color = GRAYN,
              hjust = 1.1, vjust = -.3) +
    geom_point(aes(color = status, fill = status, shape = status),
               size = 1.7, stroke = .6) +
    scale_shape_manual(values = c(retained = 16,
                                  `reclassified inconclusive` = 21),
                       name = NULL) +
    scale_color_manual(values = c(retained = TEAL,
                                  `reclassified inconclusive` = RUST),
                       name = NULL) +
    scale_fill_manual(values = c(retained = TEAL,
                                 `reclassified inconclusive` = "white"),
                      name = NULL) +
    labs(x = "design noise (SD)", y = "decline signal (CDF pts)",
         title = "C.  Why countries reclassify") +
    coord_cartesian(xlim = c(0, lim), ylim = c(0, max(pair$signal) * 1.12)) +
    thm() + theme(legend.position = c(.03, .97),
                  legend.justification = c(0, 1),
                  legend.key.size = unit(.3, "cm"),
                  legend.background = element_blank())
  # B. UpSet
  pats <- cty |>
    count(marginal = any_plugin, `any-pair` = any_da, net = net_da,
          persistent = persist_da, name = "n") |>
    arrange(desc(n)) |> mutate(px = row_number())
  bars <- ggplot(pats, aes(px, n)) +
    geom_col(fill = NAVY, width = .58) +
    geom_text(aes(label = n), vjust = -.4, size = 2.7, color = "#222222") +
    scale_y_continuous(limits = c(0, max(pats$n) * 1.2)) +
    scale_x_continuous(limits = c(.4, nrow(pats) + .6), expand = c(0, 0)) +
    labs(y = "countries", x = NULL, title = "B.  Countries by claim set") +
    thm() + theme(axis.text.x = element_blank(),
                  panel.grid.major.x = element_blank())
  dots <- pats |>
    pivot_longer(c(marginal, `any-pair`, net, persistent),
                 names_to = "set", values_to = "on") |>
    mutate(set = factor(set, levels = rev(c("marginal", "any-pair", "net",
                                            "persistent"))))
  seg <- dots |> filter(on) |> group_by(px) |>
    summarise(ymin = min(as.integer(set)), ymax = max(as.integer(set)))
  mat <- ggplot(dots, aes(px, set)) +
    geom_point(aes(alpha = on), size = 2.1, color = NAVY) +
    geom_point(data = filter(dots, !on), size = 2.1, shape = 21,
               color = "grey80", fill = "white", stroke = .5) +
    geom_segment(data = seg, aes(x = px, xend = px, y = ymin, yend = ymax),
                 inherit.aes = FALSE, color = NAVY, size = .5) +
    scale_alpha_manual(values = c(`TRUE` = 1, `FALSE` = 0), guide = "none") +
    scale_x_continuous(limits = c(.4, nrow(pats) + .6), expand = c(0, 0)) +
    labs(x = NULL, y = NULL) +
    thm() + theme(panel.grid = element_blank(),
                  axis.text.x = element_blank())
  B <- plot_grid(bars, mat, ncol = 1, rel_heights = c(1.15, .8),
                 align = "v", axis = "lr")
  fig <- plot_grid(plot_grid(A, C, nrow = 1, rel_widths = c(1, 1.25)),
                   B, ncol = 1, rel_heights = c(1.15, 1))
  ggsave("paper/figures/guarantee_hierarchy.pdf", fig, width = 5.5,
         height = 4.6, device = cairo_pdf, bg = "white")
  ggsave("paper/figures/guarantee_hierarchy.png", fig, width = 5.5,
         height = 4.6, dpi = 300, bg = "white")
}

## ---------------------------------------------------------------- Figure 4
fig4 <- function() {
  core <- read_csv("results/certified_core.csv", show_col_types = FALSE) |>
    mutate(core = lb(core))
  mags <- read_csv("results/wvs_core_magnitudes.csv",
                   show_col_types = FALSE) |>
    mutate(certified = lb(certified))
  w <- read_csv("results/wvs_deconsolidation.csv", show_col_types = FALSE) |>
    mutate(item_label = c("democracy", "strong leader", "army rule",
                          "dem. system", "parliament"))
  # A. slope
  sl <- w |> transmute(item_label, `marginal\nwave-pair` = anypair_plugin,
                       `persistent\nplug-in` = persist_plugin,
                       `persistent\ndesign-aware` = persist) |>
    pivot_longer(-item_label, names_to = "stage", values_to = "n") |>
    mutate(stage = factor(stage, levels = c("marginal\nwave-pair",
                                            "persistent\nplug-in",
                                            "persistent\ndesign-aware")))
  A <- ggplot(sl, aes(stage, n, group = item_label)) +
    geom_line(color = "grey60", size = .45) +
    geom_point(color = NAVY, size = 1.6) +
    geom_text_repel(data = filter(sl, as.integer(stage) == 3),
                    aes(label = item_label), size = 2.5, color = "grey30",
                    direction = "y", nudge_x = .45, segment.color = NA) +
    labs(x = NULL, y = "countries certified",
         title = "A.  The claim discipline, per item") +
    scale_x_discrete(expand = expansion(mult = c(.08, .42))) +
    thm() + theme(axis.text.x = element_text(size = 7.0))
  # B. map
  wmap <- st_read("pcb/figures/assets/ne_110m_countries.geojson",
                  quiet = TRUE) |>
    mutate(iso = suppressWarnings(as.integer(ISO_N3))) |>
    left_join(core |> select(iso, n_items, core), by = "iso") |>
    mutate(n = replace_na(n_items, 0),
           corec = replace_na(core, FALSE))
  B <- ggplot(wmap) +
    geom_sf(aes(fill = factor(pmin(n, 4))), color = "white",
            size = .08) +
    geom_sf(data = filter(wmap, corec), fill = NA, color = NAVY,
            size = .45) +
    scale_fill_manual(values = SEQ5, name = "certified items",
                      labels = c("0", "1", "2", "3", "4")) +
    coord_sf(ylim = c(-56, 84), expand = FALSE, datum = NA) +
    labs(title = "B.  Where certification concentrates") +
    theme_void() +
    theme(plot.title = element_text(size = 9.5, face = "bold", hjust = 0),
          legend.position = "bottom",
          legend.key.size = unit(.3, "cm"),
          legend.text = element_text(size = 7.2),
          legend.title = element_text(size = 7.6))
  # C. magnitude matrix
  items <- c("imp_dem", "rej_leader", "rej_army", "sup_demsys",
             "confid_parl")
  ilabs <- c("democracy\nessential", "reject strong\nleader",
             "reject army\nrule", "democratic\nsystem",
             "confidence in\nparliament")
  cc <- core |> filter(core) |>
    arrange(desc(n_items), country) |> mutate(row = row_number())
  cm <- expand_grid(iso = cc$iso, item = items) |>
    left_join(cc |> select(iso, country, row, n_items), by = "iso") |>
    left_join(mags |> filter(certified) |>
                select(iso, item, magnitude_lb), by = c("iso", "item")) |>
    mutate(item = factor(item, levels = items, labels = ilabs))
  C <- ggplot(cm, aes(item, reorder(country, -row))) +
    geom_point(data = filter(cm, is.na(magnitude_lb)), size = .8,
               color = "grey85") +
    geom_point(data = filter(cm, !is.na(magnitude_lb)),
               aes(size = magnitude_lb), color = TEAL, alpha = .9) +
    geom_text(data = cc, aes(x = 5.75, y = reorder(country, -row),
                             label = n_items),
              inherit.aes = FALSE, size = 2.7, fontface = "bold",
              color = "#222222") +
    annotate("text", x = 5.75, y = nrow(cc) + .8, label = "# items",
             size = 2.5, color = GRAYN, fontface = 3) +
    scale_size_area(max_size = 7.5, breaks = c(.02, .1, .3),
                    name = "certified decline (CDF pts)") +
    scale_x_discrete(position = "top",
                     expand = expansion(add = c(.6, 1.1))) +
    coord_cartesian(ylim = c(.6, nrow(cc) + 1.1), clip = "off") +
    labs(x = NULL, y = NULL,
         title = "C.  The certified core, by evidence strength") +
    thm() + theme(panel.grid.major = element_blank(),
                  axis.text.x = element_text(size = 7.0),
                  legend.position = "bottom",
                  legend.key.size = unit(.3, "cm"))
  fig <- plot_grid(plot_grid(A, B, nrow = 1, rel_widths = c(1, 1.5)),
                   C, ncol = 1, rel_heights = c(1, 1.6))
  ggsave("paper/figures/certified_core.pdf", fig, width = 5.5,
         height = 6.6, device = cairo_pdf, bg = "white")
  ggsave("paper/figures/certified_core.png", fig, width = 5.5,
         height = 6.6, dpi = 300, bg = "white")
}

fig1(); fig2(); fig3(); fig4()
cat("wrote 4 main figures to paper/figures/\n")
