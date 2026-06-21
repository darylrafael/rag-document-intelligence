from typing import List, Dict, Any, Optional
from datetime import datetime
import sqlite3
from backend.db.database import get_db_connection
from backend.models.schemas import DocumentResponse, QueryHistoryItem, DocumentQueryCount, AnalyticsStatsResponse

def parse_row_dates(row_dict: dict) -> dict:
    for field in ["indexed_at", "timestamp"]:
        if field in row_dict and isinstance(row_dict[field], str):
            row_dict[field] = datetime.fromisoformat(row_dict[field])
    return row_dict

def insert_document(doc_id: str, filename: str, file_type: str, chunk_count: int, file_size_kb: float):
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO documents (id, filename, file_type, chunk_count, file_size_kb, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (doc_id, filename, file_type, chunk_count, file_size_kb, 'indexed'))
        conn.commit()
    finally:
        conn.close()

def get_all_documents() -> List[DocumentResponse]:
    conn = get_db_connection()
    try:
        cursor = conn.execute('SELECT * FROM documents ORDER BY indexed_at DESC')
        rows = cursor.fetchall()
        return [DocumentResponse(**parse_row_dates(dict(row))) for row in rows]
    finally:
        conn.close()

def get_document(doc_id: str) -> Optional[DocumentResponse]:
    conn = get_db_connection()
    try:
        cursor = conn.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
        row = cursor.fetchone()
        if row:
            return DocumentResponse(**parse_row_dates(dict(row)))
        return None
    finally:
        conn.close()

def delete_document_record(doc_id: str):
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
        conn.commit()
    finally:
        conn.close()

def record_query(query_id: str, question: str, confidence_score: int, referenced_doc_ids: List[str]):
    conn = get_db_connection()
    try:
        # Insert the query
        conn.execute('''
            INSERT INTO queries (id, question, confidence_score, doc_count)
            VALUES (?, ?, ?, ?)
        ''', (query_id, question, confidence_score, len(set(referenced_doc_ids))))
        
        # Insert document references for analytics
        for doc_id in set(referenced_doc_ids):
            conn.execute('''
                INSERT INTO query_documents (query_id, doc_id)
                VALUES (?, ?)
            ''', (query_id, doc_id))
            
        conn.commit()
    finally:
        conn.close()

def get_query_history(page: int = 1, size: int = 20) -> List[QueryHistoryItem]:
    conn = get_db_connection()
    try:
        offset = (page - 1) * size
        cursor = conn.execute('''
            SELECT id as query_id, question, timestamp, confidence_score, doc_count 
            FROM queries 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        ''', (size, offset))
        rows = cursor.fetchall()
        return [QueryHistoryItem(**parse_row_dates(dict(row))) for row in rows]
    finally:
        conn.close()

def get_total_queries_count() -> int:
    conn = get_db_connection()
    try:
        cursor = conn.execute('SELECT COUNT(*) as count FROM queries')
        row = cursor.fetchone()
        return row['count'] if row else 0
    finally:
        conn.close()

def get_analytics_stats() -> AnalyticsStatsResponse:
    conn = get_db_connection()
    try:
        # Total docs
        cursor = conn.execute('SELECT COUNT(*) as count FROM documents')
        total_docs = cursor.fetchone()['count']
        
        # Total queries and avg confidence
        cursor = conn.execute('SELECT COUNT(*) as count, AVG(confidence_score) as avg_conf FROM queries')
        q_row = cursor.fetchone()
        total_queries = q_row['count'] if q_row['count'] else 0
        avg_confidence = q_row['avg_conf'] if q_row['avg_conf'] is not None else 0.0
        
        # Most queried docs
        cursor = conn.execute('''
            SELECT d.id as doc_id, d.filename, COUNT(qd.query_id) as query_count
            FROM documents d
            JOIN query_documents qd ON d.id = qd.doc_id
            GROUP BY d.id, d.filename
            ORDER BY query_count DESC
            LIMIT 5
        ''')
        mq_rows = cursor.fetchall()
        most_queried_docs = [DocumentQueryCount(**dict(row)) for row in mq_rows]
        
        return AnalyticsStatsResponse(
            total_docs=total_docs,
            total_queries=total_queries,
            avg_confidence=float(avg_confidence),
            most_queried_docs=most_queried_docs
        )
    finally:
        conn.close()
