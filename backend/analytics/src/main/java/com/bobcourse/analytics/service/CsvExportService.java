package com.bobcourse.analytics.service;

import com.bobcourse.analytics.dto.CampaignStatsRequest;
import com.bobcourse.analytics.dto.CampaignStatsResponse;
import com.bobcourse.analytics.dto.CsvExportRequest;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.Map;

/**
 * Generates privacy-preserving aggregated CSV reports.
 * Individual submissions and submission indexes are never exported.
 */
@Service
public class CsvExportService {

    private static final String LINE_SEP = "\n";
    private static final String COMMA = ",";

    private final CampaignStatsService campaignStatsService;

    public CsvExportService(CampaignStatsService campaignStatsService) {
        this.campaignStatsService = campaignStatsService;
    }

    public String generate(CsvExportRequest request) {
        StringBuilder sb = new StringBuilder();

        sb.append(
            "question_id,question_text,average_rating," +
            "rating_1,rating_2,rating_3,rating_4,rating_5,total_responses"
        ).append(LINE_SEP);

        CampaignStatsRequest statsRequest = new CampaignStatsRequest();
        statsRequest.setCampaignId(request.getCampaignId());
        statsRequest.setCourseCode(request.getCourseCode());
        statsRequest.setCourseName(request.getCourseName());
        statsRequest.setTotalEnrolled(0);
        statsRequest.setSubmissions(request.getSubmissions());

        CampaignStatsResponse stats =
                campaignStatsService.compute(statsRequest);

        if (stats.getQuestionStats() == null ||
                stats.getQuestionStats().isEmpty()) {
            return sb.toString();
        }

        for (CampaignStatsResponse.QuestionStats question :
                stats.getQuestionStats()) {

            Map<Integer, Long> distribution =
                    question.getDistribution() == null
                            ? Collections.emptyMap()
                            : question.getDistribution();

            long totalResponses = 0;

            for (int rating = 1; rating <= 5; rating++) {
                totalResponses += distribution.getOrDefault(rating, 0L);
            }

            sb.append(escapeCsv(question.getQuestionId())).append(COMMA)
              .append(escapeCsv(question.getQuestionText())).append(COMMA)
              .append(question.getAverage()).append(COMMA)
              .append(distribution.getOrDefault(1, 0L)).append(COMMA)
              .append(distribution.getOrDefault(2, 0L)).append(COMMA)
              .append(distribution.getOrDefault(3, 0L)).append(COMMA)
              .append(distribution.getOrDefault(4, 0L)).append(COMMA)
              .append(distribution.getOrDefault(5, 0L)).append(COMMA)
              .append(totalResponses)
              .append(LINE_SEP);
        }

        return sb.toString();
    }

    private String escapeCsv(String value) {
        if (value == null) {
            return "";
        }

        if (value.contains(",") ||
                value.contains("\"") ||
                value.contains("\n")) {
            return "\"" + value.replace("\"", "\"\"") + "\"";
        }

        return value;
    }
}
