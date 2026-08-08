package com.bobcourse.analytics.controller;

import com.bobcourse.analytics.dto.*;
import com.bobcourse.analytics.service.*;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * Internal analytics controller — called by Python only.
 * All endpoints are POST (Python sends full data payload).
 * No direct DB access — Python provides the data.
 */
@RestController
@RequestMapping("/internal/analytics")
public class AnalyticsController {

    private final CampaignStatsService campaignStatsService;
    private final TrendService trendService;
    private final DashboardService dashboardService;
    private final CsvExportService csvExportService;

    public AnalyticsController(
            CampaignStatsService campaignStatsService,
            TrendService trendService,
            DashboardService dashboardService,
            CsvExportService csvExportService) {
        this.campaignStatsService = campaignStatsService;
        this.trendService = trendService;
        this.dashboardService = dashboardService;
        this.csvExportService = csvExportService;
    }

    /** Compute statistics for a single campaign. */
    @PostMapping("/campaign-stats")
    public ResponseEntity<CampaignStatsResponse> campaignStats(@RequestBody CampaignStatsRequest request) {
        return ResponseEntity.ok(campaignStatsService.compute(request));
    }

    /** Compute multi-semester trend data for a course. */
    @PostMapping("/course-trends")
    public ResponseEntity<TrendResponse> courseTrends(@RequestBody TrendRequest request) {
        return ResponseEntity.ok(trendService.compute(request));
    }

    /** University-wide KPI dashboard. */
    @PostMapping("/dashboard")
    public ResponseEntity<DashboardResponse> dashboard(@RequestBody DashboardRequest request) {
        return ResponseEntity.ok(dashboardService.compute(request));
    }

    /** Export campaign data as CSV. */
    @PostMapping(value = "/export-csv", produces = MediaType.TEXT_PLAIN_VALUE)
    public ResponseEntity<String> exportCsv(@RequestBody CsvExportRequest request) {
        String csv = csvExportService.generate(request);
        return ResponseEntity.ok()
                .contentType(MediaType.TEXT_PLAIN)
                .header("Content-Disposition",
                        "attachment; filename=\"campaign-" + request.getCampaignId() + ".csv\"")
                .body(csv);
    }
}
