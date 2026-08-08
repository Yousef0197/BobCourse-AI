package com.bobcourse.analytics.service;

import com.bobcourse.analytics.dto.CampaignStatsRequest;
import com.bobcourse.analytics.dto.CsvExportRequest;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class CsvExportServiceTest {

    private CsvExportService service;

    @BeforeEach
    void setUp() {
        service = new CsvExportService(new CampaignStatsService());
    }

    private CampaignStatsRequest.AnswerData answer(String qId, String qText, int rating) {
        CampaignStatsRequest.AnswerData a = new CampaignStatsRequest.AnswerData();
        a.setQuestionId(qId);
        a.setQuestionText(qText);
        a.setRating(rating);
        return a;
    }

    private CampaignStatsRequest.SubmissionData submission(
            CampaignStatsRequest.AnswerData... answers) {
        CampaignStatsRequest.SubmissionData s =
                new CampaignStatsRequest.SubmissionData();
        s.setAnswers(Arrays.asList(answers));
        return s;
    }

    @Test
    void generateCsv_containsAggregatedHeader() {
        CsvExportRequest req = new CsvExportRequest();
        req.setCampaignId("camp-001");
        req.setSubmissions(Collections.emptyList());

        String csv = service.generate(req);

        assertTrue(csv.startsWith(
                "question_id,question_text,average_rating,rating_1,rating_2,rating_3,rating_4,rating_5,total_responses"
        ));
    }

    @Test
    void generateCsv_aggregatesAnswersByQuestion() {
        CsvExportRequest req = new CsvExportRequest();
        req.setCampaignId("camp-002");
        req.setSubmissions(List.of(
                submission(
                        answer("q1", "Overall quality?", 4),
                        answer("q2", "Instructor effectiveness?", 5)
                ),
                submission(
                        answer("q1", "Overall quality?", 3),
                        answer("q2", "Instructor effectiveness?", 4)
                )
        ));

        String csv = service.generate(req);
        String[] lines = csv.split("\n");

        // 1 header + 1 aggregated row per question.
        assertEquals(3, lines.length);

        assertTrue(csv.contains(
                "q1,Overall quality?,3.5,0,0,1,1,0,2"
        ));

        assertTrue(csv.contains(
                "q2,Instructor effectiveness?,4.5,0,0,0,1,1,2"
        ));
    }

    @Test
    void generateCsv_doesNotExposeSubmissionIndexes() {
        CsvExportRequest req = new CsvExportRequest();
        req.setCampaignId("camp-003");
        req.setSubmissions(List.of(
                submission(answer("q1", "Q1", 5)),
                submission(answer("q1", "Q1", 3))
        ));

        String csv = service.generate(req);

        assertFalse(csv.contains("submission_index"));
        assertEquals(2, csv.split("\n").length);
    }

    @Test
    void generateCsv_textWithCommas_properlyEscaped() {
        CsvExportRequest req = new CsvExportRequest();
        req.setCampaignId("camp-004");
        req.setSubmissions(List.of(
                submission(answer("q1", "Rate the course, overall", 4))
        ));

        String csv = service.generate(req);

        assertTrue(csv.contains("\"Rate the course, overall\""));
    }
}

