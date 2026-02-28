from src.app.models.classifier import classifier_instance
from src.app.utils.constants import (
    LABEL_MAPPING, MIN_THRESHOLD, 
    CONFIDENCE_THRESHOLD, SEVERITY_THRESHOLD
)
from src.app.utils.llm import generate_reason, correct_comment_text
from src.app.schemas.comment import CommentFeedbackResponse

class CommentService:
    """댓글 분석 서비스"""
    
    @staticmethod
    def classify(text: str) -> dict:
        """혐오 표현 분류 (모델)"""
        
        # 모델로 분류
        result = classifier_instance.predict(text)
        all_labels = result[0] if result and result[0] else []
        sorted_labels = sorted(all_labels, key=lambda x: x['score'], reverse=True)
        
        # 필터링
        significant_labels = [r for r in sorted_labels if r['score'] >= MIN_THRESHOLD]
        confidence = sorted_labels[0]['score'] if sorted_labels else 0.0
        is_problematic = any(r['score'] >= CONFIDENCE_THRESHOLD for r in all_labels)
        
        # 심각도 판정
        if confidence >= SEVERITY_THRESHOLD:
            severity = "높음"
        elif confidence >= 0.4:
            severity = "중간"
        else:
            severity = "낮음"
        
        # 한글 라벨로 변환
        problem_types = [
            LABEL_MAPPING.get(r['label'], r['label']) 
            for r in significant_labels
        ]
        
        return {
            "is_problematic": is_problematic,
            "severity": severity,
            "problem_types": problem_types,
            "confidence": round(confidence, 2),
            "issue_count": len(significant_labels),
            "all_labels": sorted_labels,  # 원본 라벨 (reason 생성용)
        }
    
    @staticmethod
    async def get_feedback(text: str) -> CommentFeedbackResponse:
        """상세 피드백 (모델 + LLM)"""
        
        # 1단계: 모델로 분류
        classification = CommentService.classify(text)
        
        # 2단계: reason 분기 처리 (하드코딩 vs API)
        if classification["is_problematic"]:
            reason = await generate_reason(
                text, 
                classification["problem_types"],
                classification["all_labels"]
            )
        else:
            reason = "문제 없는 표현입니다."
        
        # 응답 생성
        return CommentFeedbackResponse.from_classification(classification, reason)
    
    @staticmethod
    async def correct(text: str) -> dict:
        """댓글 수정"""
        
        # 1단계: 분류 (문제 여부 판정)
        classification = CommentService.classify(text)
        
        # 2단계: 문제 없으면 원본 반환 (빠름!)
        if not classification["is_problematic"]:
            return {
                "corrected_comment": text,
                "is_corrected": False,
                "reason": "수정할 내용이 없습니다.",
                "classification": classification,
            }

        # 3단계: 문제 있으면 수정 생성 (느림)
        try:
            corrected = await correct_comment_text(text)
            return {
                "corrected_comment": corrected,
                "is_corrected": True,
                "reason": f"감지된 문제: {', '.join(classification['problem_types'])}",
                "classification": classification,
            }
        except Exception as e:
            # OpenAI API 오류 시 폴백
            return {
                "corrected_comment": text,
                "is_corrected": False,
                "reason": f"수정 실패: {str(e)}",
                "classification": classification,
            }