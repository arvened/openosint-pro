# 🚀 PHASE 1: OpenOSINT Pro - START!

## 📤 ФАЙЛ 1: `political_ops_detection.py`

**Репо:** github.com/arvened/openosint-pro

---

### ✅ ШАГ 1: ОТКРОЙ РЕПО

На мобильном браузере перейди:
```
https://github.com/arvened/openosint-pro
```

---

### ✅ ШАГ 2: СОЗДАЙ НОВЫЙ ФАЙЛ

1. Нажми **"Add file"** (иконка + вверху)
2. Выбери **"Create new file"**

---

### ✅ ШАГ 3: ИМЯ ФАЙЛА

В поле **"Name your file"** введи:
```
political_ops_detection.py
```

---

### ✅ ШАГ 4: СКОПИРУЙ КОД

Весь код ниже — это **политический_ops_detection.py**

Скопируй в поле контента (весь файл ниже):

```python
"""
Political Operations Detection Module
OpenOSINT Pro - Detect coordinated inauthentic behavior, PSYOP, information operations
Based on analysis framework by Vladislav Smirnov (OSINT methodology)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import asyncio
from datetime import datetime, timedelta
import hashlib
import re
from collections import Counter, defaultdict


class OperationType(Enum):
    """Classification of political operations"""
    CIB = "coordinated_inauthentic_behavior"
    PSYOP = "psychological_operation"
    FIMI = "foreign_information_manipulation"
    DISINFORMATION = "disinformation"
    FRAME_CONTROL = "frame_control"
    AMPLIFICATION = "amplification"
    UNKNOWN = "unknown"


class ThreatLevel(Enum):
    """Threat severity"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Account:
    """Political campaign account profile"""
    account_id: str
    username: str
    created_date: datetime
    post_count: int
    follower_count: int
    posts: List[Dict] = field(default_factory=list)
    location: Optional[str] = None
    verified: bool = False
    bio: Optional[str] = None
    
    def age_days(self) -> int:
        """Account age in days"""
        return (datetime.now() - self.created_date).days
    
    def posting_frequency(self) -> float:
        """Posts per day"""
        if self.age_days() == 0:
            return self.post_count
        return self.post_count / self.age_days()
    
    def engagement_ratio(self) -> float:
        """Posts relative to followers"""
        if self.follower_count == 0:
            return 0.0
        return self.post_count / self.follower_count


@dataclass
class Post:
    """Social media post"""
    post_id: str
    account_id: str
    content: str
    timestamp: datetime
    likes: int
    reposts: int
    replies: int
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)
    
    def engagement_score(self) -> int:
        """Total engagement"""
        return self.likes + self.reposts + self.replies
    
    def hash_content(self) -> str:
        """Content fingerprint (for duplicate detection)"""
        normalized = re.sub(r'\s+', '', self.content.lower())
        return hashlib.sha256(normalized.encode()).hexdigest()


@dataclass
class CIBCluster:
    """Coordinated inauthentic behavior cluster"""
    cluster_id: str
    accounts: List[Account]
    common_patterns: List[str]
    temporal_coordination: float
    content_similarity: float
    timing_precision: float
    threat_level: ThreatLevel
    confidence: float


@dataclass
class PoliticalOperation:
    """Detected political operation"""
    operation_id: str
    operation_type: OperationType
    subject: str
    campaigns: List[str]
    accounts_involved: List[str]
    start_date: datetime
    end_date: Optional[datetime]
    threat_level: ThreatLevel
    confidence: float
    indicators: Dict[str, float]
    cib_clusters: List[CIBCluster] = field(default_factory=list)
    narrative: str = ""


class PoliticalOpsDetector:
    """Detect political operations, coordinated behavior, information warfare"""
    
    def __init__(self, 
                 cib_threshold: float = 0.65,
                 timing_tolerance_minutes: int = 15):
        self.cib_threshold = cib_threshold
        self.timing_tolerance = timedelta(minutes=timing_tolerance_minutes)
        self.operations: Dict[str, PoliticalOperation] = {}
        
    async def analyze_campaign(self, 
                              subject: str,
                              accounts: List[Account],
                              posts: List[Post]) -> PoliticalOperation:
        """Comprehensive campaign analysis"""
        cib_clusters = await self._detect_cib(accounts, posts)
        content_patterns = self._analyze_content_patterns(posts)
        timing_scores = self._analyze_timing_coordination(posts)
        narratives = self._extract_narratives(posts)
        threat = self._assess_threat_level(cib_clusters, content_patterns, timing_scores)
        
        operation = PoliticalOperation(
            operation_id=f"op_{subject}_{datetime.now().isoformat()}",
            operation_type=self._classify_operation(cib_clusters, narratives),
            subject=subject,
            campaigns=self._extract_campaigns(posts),
            accounts_involved=[a.account_id for a in accounts],
            start_date=min(p.timestamp for p in posts),
            end_date=max(p.timestamp for p in posts),
            threat_level=threat,
            confidence=self._calculate_confidence(cib_clusters, content_patterns),
            indicators={
                "cib_score": max([c.confidence for c in cib_clusters], default=0.0),
                "content_similarity": self._avg_content_similarity(posts),
                "temporal_coordination": max([c.temporal_coordination for c in cib_clusters], default=0.0),
                "bot_like_behavior": self._detect_bot_patterns(accounts),
                "artificial_amplification": self._detect_amplification(posts),
            },
            cib_clusters=cib_clusters,
            narrative=narratives[0] if narratives else "Unknown"
        )
        
        self.operations[operation.operation_id] = operation
        return operation
    
    async def _detect_cib(self, accounts: List[Account], posts: List[Post]) -> List[CIBCluster]:
        """Detect Coordinated Inauthentic Behavior"""
        clusters = []
        
        if len(accounts) < 3:
            return clusters
        
        behavior_groups = self._group_by_behavior_similarity(accounts)
        
        for group in behavior_groups:
            timing_correlation = self._calculate_timing_correlation(group, posts)
            content_sim = self._calculate_content_similarity_for_group(group, posts)
            posting_pattern_score = self._detect_posting_patterns(group)
            
            if timing_correlation > 0.6 and content_sim > 0.65:
                cluster = CIBCluster(
                    cluster_id=f"cib_{len(clusters)}",
                    accounts=group,
                    common_patterns=self._extract_common_patterns(group, posts),
                    temporal_coordination=timing_correlation,
                    content_similarity=content_sim,
                    timing_precision=posting_pattern_score,
                    threat_level=ThreatLevel.HIGH if content_sim > 0.8 else ThreatLevel.MEDIUM,
                    confidence=min(timing_correlation, content_sim)
                )
                clusters.append(cluster)
        
        return clusters
    
    def _analyze_content_patterns(self, posts: List[Post]) -> Dict[str, List[str]]:
        """Анализ паттернов контента"""
        patterns = defaultdict(list)
        
        content_hashes = Counter(p.hash_content() for p in posts)
        for content_hash, count in content_hashes.most_common(10):
            if count >= 3:
                patterns["exact_duplicates"].append(f"Content appears {count} times")
        
        all_hashtags = []
        for p in posts:
            all_hashtags.extend(p.hashtags)
        hashtag_freq = Counter(all_hashtags)
        
        for tag, count in hashtag_freq.most_common(5):
            if count >= 5:
                patterns["trending_hashtags"].append(f"#{tag} ({count} uses)")
        
        keywords = self._extract_keywords(posts)
        for kw, count in keywords.most_common(10):
            if count >= 3:
                patterns["narrative_keywords"].append(f"{kw} ({count} mentions)")
        
        return patterns
    
    def _analyze_timing_coordination(self, posts: List[Post]) -> Dict[str, float]:
        """Анализ временной координации постов"""
        if len(posts) < 2:
            return {"score": 0.0}
        
        sorted_posts = sorted(posts, key=lambda p: p.timestamp)
        gaps = []
        for i in range(len(sorted_posts) - 1):
            gap = (sorted_posts[i+1].timestamp - sorted_posts[i].timestamp).total_seconds()
            gaps.append(gap)
        
        if gaps:
            avg_gap = sum(gaps) / len(gaps)
            gap_variance = sum((g - avg_gap) ** 2 for g in gaps) / len(gaps)
            regularity_score = 1.0 - min(gap_variance / (avg_gap ** 2 + 0.01), 1.0)
        else:
            regularity_score = 0.0
        
        return {"regularity_score": regularity_score}
    
    def _extract_narratives(self, posts: List[Post]) -> List[str]:
        """Extract main narratives/frames"""
        keywords = self._extract_keywords(posts)
        narratives = []
        for kw, count in keywords.most_common(5):
            if count >= 3:
                narratives.append(kw)
        return narratives or ["Generic promotion"]
    
    def _assess_threat_level(self, 
                            cib_clusters: List[CIBCluster],
                            content_patterns: Dict,
                            timing_scores: Dict) -> ThreatLevel:
        """Оценка уровня угрозы"""
        if not cib_clusters and not content_patterns.get("exact_duplicates"):
            return ThreatLevel.LOW
        
        cib_score = max([c.confidence for c in cib_clusters], default=0.0)
        
        if cib_score > 0.85:
            return ThreatLevel.CRITICAL
        elif cib_score > 0.75:
            return ThreatLevel.HIGH
        elif cib_score > 0.60:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def _calculate_confidence(self, 
                            cib_clusters: List[CIBCluster],
                            content_patterns: Dict) -> float:
        """Calculate overall confidence in detection"""
        if not cib_clusters and not content_patterns:
            return 0.0
        
        cib_confidence = max([c.confidence for c in cib_clusters], default=0.0)
        pattern_confidence = 0.5 if content_patterns.get("exact_duplicates") else 0.0
        
        return (cib_confidence * 0.6) + (pattern_confidence * 0.4)
    
    def _classify_operation(self, cib_clusters: List[CIBCluster], narratives: List[str]) -> OperationType:
        """Classify type of operation"""
        if cib_clusters:
            return OperationType.CIB
        if narratives:
            return OperationType.AMPLIFICATION
        return OperationType.UNKNOWN
    
    def _group_by_behavior_similarity(self, accounts: List[Account]) -> List[List[Account]]:
        """Group accounts with similar behavior"""
        groups = []
        used = set()
        
        for i, acc1 in enumerate(accounts):
            if i in used:
                continue
            
            group = [acc1]
            used.add(i)
            
            for j, acc2 in enumerate(accounts[i+1:], start=i+1):
                if j in used:
                    continue
                if self._behavior_similarity(acc1, acc2) > 0.65:
                    group.append(acc2)
                    used.add(j)
            
            if len(group) >= 3:
                groups.append(group)
        
        return groups
    
    def _behavior_similarity(self, acc1: Account, acc2: Account) -> float:
        """Compare account behaviors"""
        freq_diff = abs(acc1.posting_frequency() - acc2.posting_frequency()) / max(acc1.posting_frequency(), acc2.posting_frequency(), 0.1)
        freq_score = 1.0 - min(freq_diff, 1.0)
        
        engagement_diff = abs(acc1.engagement_ratio() - acc2.engagement_ratio())
        engagement_score = 1.0 - min(engagement_diff, 1.0)
        
        return (freq_score * 0.5) + (engagement_score * 0.5)
    
    def _calculate_timing_correlation(self, accounts: List[Account], posts: List[Post]) -> float:
        """Calculate how synchronized accounts post"""
        account_ids = {a.account_id for a in accounts}
        account_posts = [p for p in posts if p.account_id in account_ids]
        
        if len(account_posts) < 5:
            return 0.0
        
        time_windows = defaultdict(int)
        for post in account_posts:
            window = post.timestamp.replace(minute=0, second=0, microsecond=0)
            time_windows[window] += 1
        
        max_in_window = max(time_windows.values())
        total_posts = len(account_posts)
        
        return min(max_in_window / (total_posts / 4), 1.0)
    
    def _calculate_content_similarity_for_group(self, accounts: List[Account], posts: List[Post]) -> float:
        """Calculate average content similarity in group"""
        account_ids = {a.account_id for a in accounts}
        group_posts = [p for p in posts if p.account_id in account_ids]
        
        if len(group_posts) < 2:
            return 0.0
        
        all_hashtags = []
        for p in group_posts:
            all_hashtags.extend(p.hashtags)
        
        if not all_hashtags:
            return 0.0
        
        hashtag_freq = Counter(all_hashtags)
        common_tags = sum(count for count in hashtag_freq.values() if count >= 2)
        
        return min(common_tags / len(all_hashtags), 1.0)
    
    def _detect_posting_patterns(self, accounts: List[Account]) -> float:
        """Detect automated/regular posting patterns"""
        frequencies = [a.posting_frequency() for a in accounts]
        
        if not frequencies:
            return 0.0
        
        avg_freq = sum(frequencies) / len(frequencies)
        variance = sum((f - avg_freq) ** 2 for f in frequencies) / len(frequencies)
        regularity = 1.0 - min(variance / (avg_freq + 0.01), 1.0)
        
        return regularity
    
    def _extract_common_patterns(self, accounts: List[Account], posts: List[Post]) -> List[str]:
        """Extract common patterns in group"""
        patterns = []
        
        account_ids = {a.account_id for a in accounts}
        group_posts = [p for p in posts if p.account_id in account_ids]
        
        all_tags = []
        for p in group_posts:
            all_tags.extend(p.hashtags)
        
        common_tags = Counter(all_tags)
        for tag, count in common_tags.most_common(3):
            if count >= len(accounts) - 1:
                patterns.append(f"Shared hashtag: #{tag}")
        
        all_urls = []
        for p in group_posts:
            all_urls.extend(p.urls)
        
        common_urls = Counter(all_urls)
        for url, count in common_urls.most_common(2):
            if count >= 2:
                patterns.append(f"Shared URL: {url}")
        
        return patterns
    
    def _extract_keywords(self, posts: List[Post]) -> Counter:
        """Extract main keywords from posts"""
        keywords = []
        for post in posts:
            words = re.findall(r'\b[а-яa-z]{4,}\b', post.content.lower())
            keywords.extend(words)
        return Counter(keywords)
    
    def _avg_content_similarity(self, posts: List[Post]) -> float:
        """Average content similarity across posts"""
        if len(posts) < 2:
            return 0.0
        
        hashes = [p.hash_content() for p in posts]
        duplicates = sum(1 for h in hashes if hashes.count(h) > 1)
        
        return duplicates / len(posts)
    
    def _detect_bot_patterns(self, accounts: List[Account]) -> float:
        """Detect bot-like behavior in accounts"""
        bot_score = 0.0
        
        for acc in accounts:
            if acc.age_days() < 30 and acc.posting_frequency() > 10:
                bot_score += 0.3
            if acc.posting_frequency() > 20:
                bot_score += 0.3
            if acc.follower_count < 10 and acc.post_count > 50:
                bot_score += 0.2
        
        return min(bot_score / len(accounts) if accounts else 0.0, 1.0)
    
    def _detect_amplification(self, posts: List[Post]) -> float:
        """Detect artificial amplification"""
        if not posts:
            return 0.0
        
        amplified = 0
        for post in posts:
            if post.engagement_score() > 1000:
                amplified += 1
        
        return amplified / len(posts)
    
    def _extract_campaigns(self, posts: List[Post]) -> List[str]:
        """Extract campaign identifiers from hashtags"""
        campaigns = []
        all_tags = []
        
        for p in posts:
            all_tags.extend(p.hashtags)
        
        tag_freq = Counter(all_tags)
        for tag, count in tag_freq.most_common(5):
            if count >= 3:
                campaigns.append(tag)
        
        return campaigns
    
    def get_operation_report(self, operation_id: str) -> str:
        """Generate human-readable report"""
        op = self.operations.get(operation_id)
        if not op:
            return "Operation not found"
        
        report = f"""
╔════════════════════════════════════════════════════════════╗
║          POLITICAL OPERATION ANALYSIS REPORT               ║
╚════════════════════════════════════════════════════════════╝

OPERATION: {op.operation_id}
SUBJECT: {op.subject}
TYPE: {op.operation_type.value}
THREAT LEVEL: {op.threat_level.name}
CONFIDENCE: {op.confidence:.1%}

PERIOD: {op.start_date.date()} to {op.end_date.date() if op.end_date else 'Ongoing'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INDICATORS:
  • CIB Score: {op.indicators.get('cib_score', 0.0):.2f}
  • Content Similarity: {op.indicators.get('content_similarity', 0.0):.2f}
  • Temporal Coordination: {op.indicators.get('temporal_coordination', 0.0):.2f}
  • Bot-like Behavior: {op.indicators.get('bot_like_behavior', 0.0):.2f}
  • Artificial Amplification: {op.indicators.get('artificial_amplification', 0.0):.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ACCOUNTS INVOLVED: {len(op.accounts_involved)}
CAMPAIGNS: {', '.join(op.campaigns) or 'None detected'}
NARRATIVE: {op.narrative}

CIB CLUSTERS DETECTED: {len(op.cib_clusters)}
"""
        
        for cluster in op.cib_clusters:
            report += f"""
  Cluster {cluster.cluster_id}:
    - Accounts: {len(cluster.accounts)}
    - Temporal Coordination: {cluster.temporal_coordination:.2f}
    - Content Similarity: {cluster.content_similarity:.2f}
    - Threat: {cluster.threat_level.name}
"""
        
        report += "\n╚════════════════════════════════════════════════════════════╝\n"
        
        return report
```

---



🚀
