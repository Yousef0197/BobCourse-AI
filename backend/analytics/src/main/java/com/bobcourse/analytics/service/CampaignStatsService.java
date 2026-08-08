package com.bobcourse.analytics.service;

import com.bobcourse.analytics.dto.CampaignStatsRequest;
import com.bobcourse.analytics.dto.CampaignStatsResponse;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

/**
 * CampaignStatsService — computes per-question averages, distributions, and response rate.
 * Pure computation: no DB access. Data is provided by Python.
 */
@Service
public class CampaignStatsService {

    /**
     * Compute statistics for a single campaign.
     *
     * @param request payload from Python (student_id already stripped)
     * @return CampaignStatsResponse with per-question and overall analytics
     */
    public CampaignStatsResponse compute(CampaignStatsRequest request) {
        CampaignStatsResponse response = new CampaignStatsResponse();
        response.setCampaignId(request.getCampaignId());
        response.setCourseCode(request.getCourseCode());
        response.setCourseName(request.getCourseName());

        List<CampaignStatsRequest.SubmissionData> submissions = request.getSubmissions();
        int totalSubmissions = (submissions == null) ? 0 : submissions.size();
        int totalEnrolled = request.getTotalEnrolled();

        response.setTotalSubmissions(totalSubmissions);
        response.setTotalEnrolled(totalEnrolled);
        response.setResponseRate(totalEnrolled > 0
                ? Math.round((double) totalSubmissions / totalEnrolled * 10000.0) / 100.0
                : 0.0);

        if (submissions == null || submissions.isEmpty()) {
            response.setOverallAverage(0.0);
            response.setQuestionStats(Collections.emptyList());
            return response;
        }

        // Group answers by questionId
        Map<String, List<CampaignStatsRequest.AnswerData>> byQuestion = new LinkedHashMap<>();
        Map<String, String> questionTexts = new LinkedHashMap<>();

        for (CampaignStatsRequest.SubmissionData sub : submissions) {
            if (sub.getAnswers() == null) continue;
            for (CampaignStatsRequest.AnswerData ans : sub.getAnswers()) {
                byQuestion.computeIfAbsent(ans.getQuestionId(), k -> new ArrayList<>()).add(ans);
                questionTexts.put(ans.getQuestionId(), ans.getQuestionText());
            }
        }

        List<CampaignStatsResponse.QuestionStats> questionStatsList = new ArrayList<>();
        double totalRatingSum = 0.0;
        int totalRatingCount = 0;

        for (Map.Entry<String, List<CampaignStatsRequest.AnswerData>> entry : byQuestion.entrySet()) {
            String qId = entry.getKey();
            List<CampaignStatsRequest.AnswerData> answers = entry.getValue();

            // Average
            double avg = answers.stream()
                    .mapToInt(CampaignStatsRequest.AnswerData::getRating)
                    .average()
                    .orElse(0.0);
            avg = Math.round(avg * 100.0) / 100.0;

            // Distribution (1–5)
            Map<Integer, Long> distribution = new TreeMap<>();
            for (int i = 1; i <= 5; i++) {
                final int rating = i;
                long count = answers.stream().filter(a -> a.getRating() == rating).count();
                distribution.put(rating, count);
            }

            CampaignStatsResponse.QuestionStats qs = new CampaignStatsResponse.QuestionStats();
            qs.setQuestionId(qId);
            qs.setQuestionText(questionTexts.getOrDefault(qId, ""));
            qs.setAverage(avg);
            qs.setDistribution(distribution);
            questionStatsList.add(qs);

            totalRatingSum += avg;
            totalRatingCount++;
        }

        double overall = totalRatingCount > 0
                ? Math.round(totalRatingSum / totalRatingCount * 100.0) / 100.0
                : 0.0;
        response.setOverallAverage(overall);
        response.setQuestionStats(questionStatsList);

        return response;
    }
}
