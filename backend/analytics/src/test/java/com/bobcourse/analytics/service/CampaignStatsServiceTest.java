package com.bobcourse.analytics.service;

import com.bobcourse.analytics.dto.CampaignStatsRequest;
import com.bobcourse.analytics.dto.CampaignStatsResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class CampaignStatsServiceTest {

    private CampaignStatsService service;

    @BeforeEach
    void setUp() {
        service = new CampaignStatsService();
    }

    private CampaignStatsRequest.AnswerData answer(String qId, String qText, int rating) {
        CampaignStatsRequest.AnswerData a = new CampaignStatsRequest.AnswerData();
        a.setQuestionId(qId);
        a.setQuestionText(qText);
        a.setRating(rating);
        return a;
    }

    private CampaignStatsRequest.SubmissionData submission(CampaignStatsRequest.AnswerData... answers) {
        CampaignStatsRequest.SubmissionData s = new CampaignStatsRequest.SubmissionData();
        s.setAnswers(Arrays.asList(answers));
        return s;
    }

    @Test
    void computeWithKnownInputs_returnsCorrectAverages() {
        // 3 submissions, 1 question each: ratings 4, 5, 3 → avg = 4.0
        CampaignStatsRequest req = new CampaignStatsRequest();
        req.setCampaignId("camp-001");
        req.setCourseCode("CS101");
        req.setCourseName("Intro CS");
        req.setTotalEnrolled(4);
        req.setSubmissions(List.of(
                submission(answer("q1", "Overall quality?", 4)),
                submission(answer("q1", "Overall quality?", 5)),
                submission(answer("q1", "Overall quality?", 3))
        ));

        CampaignStatsResponse resp = service.compute(req);

        assertEquals(3, resp.getTotalSubmissions());
        assertEquals(4, resp.getTotalEnrolled());
        assertEquals(75.0, resp.getResponseRate(), 0.01); // 3/4 = 75%
        assertEquals(4.0, resp.getOverallAverage(), 0.01);
        assertEquals(1, resp.getQuestionStats().size());

        CampaignStatsResponse.QuestionStats qs = resp.getQuestionStats().get(0);
        assertEquals("q1", qs.getQuestionId());
        assertEquals(4.0, qs.getAverage(), 0.01);
        assertEquals(1L, qs.getDistribution().get(3));
        assertEquals(1L, qs.getDistribution().get(4));
        assertEquals(1L, qs.getDistribution().get(5));
        assertEquals(0L, qs.getDistribution().get(1));
        assertEquals(0L, qs.getDistribution().get(2));
    }

    @Test
    void computeMultipleQuestions_correctOverallAverage() {
        // q1 avg=4, q2 avg=2 → overall avg = 3
        CampaignStatsRequest req = new CampaignStatsRequest();
        req.setCampaignId("camp-002");
        req.setCourseCode("CS201");
        req.setCourseName("Data Structures");
        req.setTotalEnrolled(2);
        req.setSubmissions(List.of(
                submission(
                        answer("q1", "Quality?", 4),
                        answer("q2", "Difficulty?", 2)
                ),
                submission(
                        answer("q1", "Quality?", 4),
                        answer("q2", "Difficulty?", 2)
                )
        ));

        CampaignStatsResponse resp = service.compute(req);
        assertEquals(3.0, resp.getOverallAverage(), 0.01);
        assertEquals(100.0, resp.getResponseRate(), 0.01);
    }

    @Test
    void computeEmptySubmissions_returnsZeros() {
        CampaignStatsRequest req = new CampaignStatsRequest();
        req.setCampaignId("camp-003");
        req.setCourseCode("CS301");
        req.setCourseName("Algorithms");
        req.setTotalEnrolled(10);
        req.setSubmissions(Collections.emptyList());

        CampaignStatsResponse resp = service.compute(req);
        assertEquals(0, resp.getTotalSubmissions());
        assertEquals(0.0, resp.getOverallAverage());
        assertEquals(0.0, resp.getResponseRate());
    }

    @Test
    void computeResponseRate_zeroEnrolled_doesNotThrow() {
        CampaignStatsRequest req = new CampaignStatsRequest();
        req.setCampaignId("camp-004");
        req.setCourseCode("CS401");
        req.setCourseName("OS");
        req.setTotalEnrolled(0);
        req.setSubmissions(Collections.emptyList());

        CampaignStatsResponse resp = service.compute(req);
        assertEquals(0.0, resp.getResponseRate());
    }
}
