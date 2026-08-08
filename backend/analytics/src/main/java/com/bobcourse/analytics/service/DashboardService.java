package com.bobcourse.analytics.service;

import com.bobcourse.analytics.dto.DashboardRequest;
import com.bobcourse.analytics.dto.DashboardResponse;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * DashboardService — university-wide KPIs.
 */
@Service
public class DashboardService {

    public DashboardResponse compute(DashboardRequest request) {
        DashboardResponse response = new DashboardResponse();

        List<DashboardRequest.CampaignSummary> campaigns = request.getCampaigns();
        if (campaigns == null || campaigns.isEmpty()) {
            response.setTotalCampaigns(0);
            response.setActiveCampaigns(0);
            response.setTotalSubmissions(0);
            response.setAverageRating(0.0);
            response.setOverallResponseRate(0.0);
            return response;
        }

        int totalCampaigns = campaigns.size();
        long activeCampaigns = campaigns.stream()
                .filter(c -> "open".equalsIgnoreCase(c.getStatus()))
                .count();

        int totalSubmissions = campaigns.stream()
                .mapToInt(DashboardRequest.CampaignSummary::getSubmissions)
                .sum();

        int totalEnrolled = campaigns.stream()
                .mapToInt(DashboardRequest.CampaignSummary::getEnrolled)
                .sum();

        // Weighted average rating across all campaigns with submissions
        double weightedSum = 0.0;
        int weightedCount = 0;
        for (DashboardRequest.CampaignSummary c : campaigns) {
            if (c.getSubmissions() > 0) {
                weightedSum += c.getAverageRating() * c.getSubmissions();
                weightedCount += c.getSubmissions();
            }
        }
        double averageRating = weightedCount > 0
                ? Math.round(weightedSum / weightedCount * 100.0) / 100.0
                : 0.0;

        double responseRate = totalEnrolled > 0
                ? Math.round((double) totalSubmissions / totalEnrolled * 10000.0) / 100.0
                : 0.0;

        response.setTotalCampaigns(totalCampaigns);
        response.setActiveCampaigns((int) activeCampaigns);
        response.setTotalSubmissions(totalSubmissions);
        response.setAverageRating(averageRating);
        response.setOverallResponseRate(responseRate);

        return response;
    }
}
