# 🚀 PHASE 1: OpenOSINT Pro - ФАЙЛ 2

## 📤 ФАЙЛ 2: `test_political_ops_detection.py`

**Репо:** github.com/arvened/openosint-pro

---

### ✅ ШАГ 1: СОЗДАЙ НОВЫЙ ФАЙЛ

1. Нажми **"Add file"** (иконка +)
2. Выбери **"Create new file"**

---

### ✅ ШАГ 2: ИМЯ ФАЙЛА

В поле **"Name your file"** введи:
```
test_political_ops_detection.py
```

---

### ✅ ШАГ 3: СКОПИРУЙ КОД

Весь текст ниже — вставь в поле:

```python
"""
Tests for Political Operations Detection Module
"""

import pytest
from datetime import datetime, timedelta
from political_ops_detection import (
    PoliticalOpsDetector, Account, Post, OperationType, ThreatLevel
)


class TestAccountBehavior:
    """Test account behavior metrics"""
    
    def test_account_age_calculation(self):
        acc = Account(
            account_id="acc1",
            username="user1",
            created_date=datetime.now() - timedelta(days=30),
            post_count=150,
            follower_count=500
        )
        
        assert 29 <= acc.age_days() <= 31
    
    def test_posting_frequency(self):
        acc = Account(
            account_id="acc1",
            username="user1",
            created_date=datetime.now() - timedelta(days=10),
            post_count=100,
            follower_count=500
        )
        
        freq = acc.posting_frequency()
        assert 9 < freq < 11
    
    def test_engagement_ratio(self):
        acc = Account(
            account_id="acc1",
            username="user1",
            created_date=datetime.now(),
            post_count=100,
            follower_count=1000
        )
        
        assert acc.engagement_ratio() == 0.1


class TestPostMetrics:
    """Test post metrics"""
    
    def test_engagement_score(self):
        post = Post(
            post_id="p1",
            account_id="acc1",
            content="Test post",
            timestamp=datetime.now(),
            likes=50,
            reposts=30,
            replies=20
        )
        
        assert post.engagement_score() == 100
    
    def test_content_hash(self):
        content = "Test content"
        post1 = Post(
            post_id="p1",
            account_id="acc1",
            content=content,
            timestamp=datetime.now(),
            likes=10,
            reposts=5,
            replies=2
        )
        
        post2 = Post(
            post_id="p2",
            account_id="acc2",
            content=content,
            timestamp=datetime.now(),
            likes=20,
            reposts=10,
            replies=5
        )
        
        assert post1.hash_content() == post2.hash_content()


@pytest.mark.asyncio
class TestCIBDetection:
    """Test coordinated inauthentic behavior detection"""
    
    async def test_detect_cib_cluster(self):
        detector = PoliticalOpsDetector()
        
        accounts = []
        base_time = datetime.now()
        
        for i in range(5):
            accounts.append(Account(
                account_id=f"acc{i}",
                username=f"user{i}",
                created_date=base_time - timedelta(days=20),
                post_count=50,
                follower_count=100
            ))
        
        posts = []
        for i, acc in enumerate(accounts):
            for j in range(10):
                posts.append(Post(
                    post_id=f"p{i}_{j}",
                    account_id=acc.account_id,
                    content="Support the campaign #Fedorov",
                    timestamp=base_time + timedelta(hours=j),
                    likes=20,
                    reposts=10,
                    replies=5,
                    hashtags=["Fedorov", "Campaign2026"]
                ))
        
        operation = await detector.analyze_campaign(
            "Fedorov",
            accounts,
            posts
        )
        
        assert operation.cib_clusters
        assert operation.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
    
    async def test_no_cib_for_diverse_accounts(self):
        detector = PoliticalOpsDetector()
        
        accounts = [
            Account(
                account_id="acc1",
                username="journalist",
                created_date=datetime.now() - timedelta(days=365),
                post_count=1000,
                follower_count=10000
            ),
            Account(
                account_id="acc2",
                username="activist",
                created_date=datetime.now() - timedelta(days=200),
                post_count=150,
                follower_count=500
            ),
            Account(
                account_id="acc3",
                username="blogger",
                created_date=datetime.now() - timedelta(days=100),
                post_count=50,
                follower_count=200
            ),
        ]
        
        posts = [
            Post(
                post_id="p1",
                account_id="acc1",
                content="Breaking news about politics",
                timestamp=datetime.now() - timedelta(days=5),
                likes=100,
                reposts=50,
                replies=30
            ),
            Post(
                post_id="p2",
                account_id="acc2",
                content="My thoughts on the election",
                timestamp=datetime.now() - timedelta(days=3),
                likes=20,
                reposts=5,
                replies=10
            ),
        ]
        
        operation = await detector.analyze_campaign(
            "Election2026",
            accounts,
            posts
        )
        
        assert operation.threat_level == ThreatLevel.LOW


class TestContentAnalysis:
    """Test content pattern analysis"""
    
    def test_detect_duplicate_content(self):
        detector = PoliticalOpsDetector()
        
        posts = [
            Post(
                post_id="p1",
                account_id="acc1",
                content="Vote for candidate X",
                timestamp=datetime.now(),
                likes=10,
                reposts=5,
                replies=2
            ),
            Post(
                post_id="p2",
                account_id="acc2",
                content="Vote for candidate X",
                timestamp=datetime.now() + timedelta(minutes=5),
                likes=15,
                reposts=8,
                replies=3
            ),
            Post(
                post_id="p3",
                account_id="acc3",
                content="Vote for candidate X",
                timestamp=datetime.now() + timedelta(minutes=10),
                likes=12,
                reposts=6,
                replies=2
            ),
        ]
        
        patterns = detector._analyze_content_patterns(posts)
        
        assert patterns["exact_duplicates"]
        assert len(patterns["exact_duplicates"]) > 0


class TestNarrativeExtraction:
    """Test narrative extraction"""
    
    def test_extract_main_narratives(self):
        detector = PoliticalOpsDetector()
        
        posts = [
            Post(
                post_id="p1",
                account_id="acc1",
                content="Fedorov is the future of Ukraine",
                timestamp=datetime.now(),
                likes=10,
                reposts=5,
                replies=2
            ),
            Post(
                post_id="p2",
                account_id="acc2",
                content="Fedorov brings innovation and technology",
                timestamp=datetime.now(),
                likes=15,
                reposts=8,
                replies=3
            ),
            Post(
                post_id="p3",
                account_id="acc3",
                content="Support Fedorov's vision",
                timestamp=datetime.now(),
                likes=12,
                reposts=6,
                replies=2
            ),
        ]
        
        narratives = detector._extract_narratives(posts)
        
        assert narratives
        assert any("fedorov" in n.lower() for n in narratives)


class TestThreatAssessment:
    """Test threat level assessment"""
    
    def test_threat_level_critical(self):
        detector = PoliticalOpsDetector()
        
        from political_ops_detection import CIBCluster
        
        cib_cluster = CIBCluster(
            cluster_id="cib1",
            accounts=[],
            common_patterns=["pattern1"],
            temporal_coordination=0.95,
            content_similarity=0.90,
            timing_precision=0.85,
            threat_level=ThreatLevel.CRITICAL,
            confidence=0.95
        )
        
        threat = detector._assess_threat_level([cib_cluster], {}, {})
        
        assert threat == ThreatLevel.CRITICAL
    
    def test_threat_level_low(self):
        detector = PoliticalOpsDetector()
        
        threat = detector._assess_threat_level([], {}, {})
        
        assert threat == ThreatLevel.LOW


@pytest.mark.asyncio
class TestReporting:
    """Test report generation"""
    
    async def test_operation_report_generation(self):
        detector = PoliticalOpsDetector()
        
        accounts = [
            Account(
                account_id="acc1",
                username="user1",
                created_date=datetime.now() - timedelta(days=10),
                post_count=50,
                follower_count=100
            ),
        ]
        
        posts = [
            Post(
                post_id="p1",
                account_id="acc1",
                content="Test message",
                timestamp=datetime.now(),
                likes=10,
                reposts=5,
                replies=2
            ),
        ]
        
        operation = await detector.analyze_campaign("Test", accounts, posts)
        report = detector.get_operation_report(operation.operation_id)
        
        assert "POLITICAL OPERATION" in report
        assert "Test" in report
        assert operation.operation_id in report


class TestBotDetection:
    """Test bot-like behavior detection"""
    
    def test_detect_bot_new_account_high_activity(self):
        detector = PoliticalOpsDetector()
        
        accounts = [
            Account(
                account_id="acc1",
                username="bot",
                created_date=datetime.now() - timedelta(days=5),
                post_count=200,
                follower_count=50
            ),
        ]
        
        bot_score = detector._detect_bot_patterns(accounts)
        
        assert bot_score > 0.5
    
    def test_detect_legitimate_account(self):
        detector = PoliticalOpsDetector()
        
        accounts = [
            Account(
                account_id="acc1",
                username="journalist",
                created_date=datetime.now() - timedelta(days=365),
                post_count=100,
                follower_count=5000
            ),
        ]
        
        bot_score = detector._detect_bot_patterns(accounts)
        
        assert bot_score < 0.3


class TestKeywordExtraction:
    """Test keyword and pattern extraction"""
    
    def test_extract_keywords(self):
        detector = PoliticalOpsDetector()
        
        posts = [
            Post(
                post_id="p1",
                account_id="acc1",
                content="Fedorov technology innovation future",
                timestamp=datetime.now(),
                likes=10,
                reposts=5,
                replies=2
            ),
            Post(
                post_id="p2",
                account_id="acc2",
                content="Fedorov technology reform change",
                timestamp=datetime.now(),
                likes=15,
                reposts=8,
                replies=3
            ),
        ]
        
        keywords = detector._extract_keywords(posts)
        
        assert "fedorov" in keywords
        assert keywords["technology"] >= 2


class TestTimingAnalysis:
    """Test timing coordination analysis"""
    
    def test_detect_synchronized_posting(self):
        detector = PoliticalOpsDetector()
        
        base_time = datetime.now()
        
        posts = [
            Post(
                post_id="p1",
                account_id="acc1",
                content="Message",
                timestamp=base_time,
                likes=10,
                reposts=5,
                replies=2
            ),
            Post(
                post_id="p2",
                account_id="acc2",
                content="Message",
                timestamp=base_time + timedelta(minutes=3),
                likes=10,
                reposts=5,
                replies=2
            ),
            Post(
                post_id="p3",
                account_id="acc3",
                content="Message",
                timestamp=base_time + timedelta(minutes=5),
                likes=10,
                reposts=5,
                replies=2
            ),
        ]
        
        timing_scores = detector._analyze_timing_coordination(posts)
        
        assert "regularity_score" in timing_scores


class TestAmplificationDetection:
    """Test artificial amplification detection"""
    
    def test_detect_artificial_engagement(self):
        detector = PoliticalOpsDetector()
        
        posts = [
            Post(
                post_id="p1",
                account_id="acc1",
                content="Small account message",
                timestamp=datetime.now(),
                likes=5000,
                reposts=2000,
                replies=1000
            ),
            Post(
                post_id="p2",
                account_id="acc2",
                content="Normal post",
                timestamp=datetime.now(),
                likes=50,
                reposts=20,
                replies=10
            ),
        ]
        
        amplification = detector._detect_amplification(posts)
        
        assert amplification > 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

