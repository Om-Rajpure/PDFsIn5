import React from 'react';
import {
    DndContext,
    closestCenter,
    KeyboardSensor,
    PointerSensor,
    useSensor,
    useSensors,
} from '@dnd-kit/core';
import {
    arrayMove,
    SortableContext,
    sortableKeyboardCoordinates,
    rectSortingStrategy,
} from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { FiTrash2, FiMove } from 'react-icons/fi';
import '../styles/OrganizeWorkspace.css';

const SortableItem = ({ id, pageIndex, imageSrc, onDelete }) => {
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({ id: id.toString() });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        zIndex: isDragging ? 100 : 1,
        opacity: isDragging ? 0.8 : 1,
    };

    return (
        <div ref={setNodeRef} style={style} className={`org-page-card ${isDragging ? 'dragging' : ''}`}>
            <div className="org-page-card__overlay">
                <button
                    className="org-page-card__delete"
                    onClick={(e) => {
                        e.stopPropagation();
                        onDelete(id);
                    }}
                    title="Remove page"
                >
                    <FiTrash2 />
                </button>
            </div>
            <img src={imageSrc} alt={`Page ${pageIndex}`} className="org-page-card__img" draggable={false} />
            <div className="org-page-card__footer" {...attributes} {...listeners}>
                <FiMove className="org-page-card__drag-handle" />
                <span className="org-page-card__label">Page {pageIndex}</span>
            </div>
        </div>
    );
};

export default function OrganizeWorkspace({ pageOrder, setPageOrder, pagePreviews }) {
    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: {
                distance: 5,
            },
        }),
        useSensor(KeyboardSensor, {
            coordinateGetter: sortableKeyboardCoordinates,
        })
    );

    const handleDragEnd = (event) => {
        const { active, over } = event;
        if (!over) return;
        if (active.id !== over.id) {
            setPageOrder((items) => {
                const oldIndex = items.indexOf(parseInt(active.id, 10));
                const newIndex = items.indexOf(parseInt(over.id, 10));
                return arrayMove(items, oldIndex, newIndex);
            });
        }
    };

    const handleDelete = (id) => {
        setPageOrder((prev) => prev.filter((p) => p !== parseInt(id, 10)));
    };

    if (!pagePreviews || pagePreviews.length === 0) return null;

    return (
        <div className="org-workspace">
            <div className="org-workspace__header">
                <p>Drag pages to reorder them or click the trash icon to remove unwanted pages.</p>
                <span className="org-workspace__count">{pageOrder.length} Pages</span>
            </div>
            <DndContext
                sensors={sensors}
                collisionDetection={closestCenter}
                onDragEnd={handleDragEnd}
            >
                <div className="org-workspace__grid">
                    <SortableContext
                        items={pageOrder.map(String)}
                        strategy={rectSortingStrategy}
                    >
                        {pageOrder.map((pageNum) => (
                            <SortableItem
                                key={pageNum}
                                id={pageNum}
                                pageIndex={pageNum}
                                imageSrc={pagePreviews[pageNum - 1]}
                                onDelete={handleDelete}
                            />
                        ))}
                    </SortableContext>
                </div>
            </DndContext>
        </div>
    );
}
